#!/bin/bash

# Exit on error
set -e

# Load environment variables
export AWS_REGION="us-east-1"
export AWS_ACCOUNT="954976318202"
export EKS_CLUSTER="idp"
export NAMESPACE="watcher"

# Function to check if a command exists
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is required but not installed."
        exit 1
    fi
}

# Check required commands
check_command aws
check_command terraform
check_command kubectl

# Function to check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "Error: AWS credentials not configured or invalid."
        echo "Please run 'aws configure' first."
        exit 1
    fi
}

# Check AWS credentials
check_aws_credentials

echo "🚀 Starting cluster setup..."

# Navigate to dependencies directory
cd "$(dirname "$0")/../infra/dependencies"

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init

# Create Terraform plan
echo "📝 Creating Terraform plan..."
terraform plan -out=tfplan

# Apply Terraform changes
echo "🔨 Applying Terraform changes..."
terraform apply -auto-approve tfplan

# Check if EKS cluster exists
echo "🔍 Checking if EKS cluster exists..."
if aws eks describe-cluster --name "$EKS_CLUSTER" --region "$AWS_REGION" &> /dev/null; then
    echo "✅ EKS cluster '$EKS_CLUSTER' already exists."
else
    echo "❌ EKS cluster '$EKS_CLUSTER' does not exist. Please run the setup-cluster.sh script first."
    exit 1
fi

# Wait for EKS cluster to be ready
echo "⏳ Waiting for EKS cluster to be ready..."
aws eks wait cluster-active --name "$EKS_CLUSTER" --region "$AWS_REGION"

# Update kubeconfig
echo "🔧 Updating kubeconfig..."
aws eks update-kubeconfig --name "$EKS_CLUSTER" --region "$AWS_REGION"

# Create namespace
echo "📁 Creating namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Check if ArgoCD is already installed
echo "🔍 Checking if ArgoCD is already installed..."
if kubectl get deployment argocd-server -n argocd &> /dev/null; then
    echo "✅ ArgoCD is already installed."
else
    # Install ArgoCD
    echo "📦 Installing ArgoCD..."
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

    # Wait for ArgoCD to be ready
    echo "⏳ Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=Available deployment/argocd-server -n argocd --timeout=300s

    # Get ArgoCD admin password and store it in SSM Parameter Store
    echo "🔑 Storing ArgoCD admin password in SSM Parameter Store..."
    ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
    aws ssm put-parameter \
        --name "/watcher/argocd/admin-password" \
        --value "$ARGOCD_PASSWORD" \
        --type SecureString \
        --overwrite \
        --region "$AWS_REGION"
fi

# Patch ArgoCD service to use NodePort
echo "🔧 Patching ArgoCD service to use NodePort..."
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'

# Get the NodePort
echo "🔍 Getting ArgoCD NodePort..."
ARGOCD_PORT=$(kubectl get svc argocd-server -n argocd -o jsonpath='{.spec.ports[0].nodePort}')
if [ -z "$ARGOCD_PORT" ]; then
    echo "⚠️ Could not get NodePort. You may need to check the service status manually."
    echo "Run: kubectl get svc argocd-server -n argocd"
else
    echo "🌐 ArgoCD UI will be available at: https://localhost:$ARGOCD_PORT"
fi

# Deploy the watcher application
echo "📦 Deploying watcher application..."
cd "$(dirname "$0")/.."
if [ -f "infra/argocd/watcher.yaml" ]; then
    kubectl apply -f infra/argocd/watcher.yaml
    echo "✅ Watcher application deployed successfully!"
else
    echo "⚠️ Watcher application manifest not found at infra/argocd/watcher.yaml"
    echo "Please create the manifest and apply it manually."
fi

echo "✅ Cluster setup completed successfully!"
if [ -n "$ARGOCD_PORT" ]; then
    echo "🌐 ArgoCD UI will be available at: https://localhost:$ARGOCD_PORT"
else
    echo "⚠️ Could not determine ArgoCD UI URL. You may need to check the service status manually."
    echo "Run: kubectl get svc argocd-server -n argocd"
fi
echo "🔑 ArgoCD admin password has been stored in SSM Parameter Store at: /watcher/argocd/admin-password" 