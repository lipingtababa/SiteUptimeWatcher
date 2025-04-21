#!/bin/bash

# Exit on error
set -e

# Load environment variables
export AWS_REGION="us-east-1"
export EKS_CLUSTER="idp"
export NAMESPACE="watcher"

# take a parameter for stage
export STAGE=$1
# default should be dev
if [ -z "$STAGE" ]; then
    export STAGE="dev"
fi

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

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
cd "$PROJECT_ROOT/infra/dependencies"

# Initialize Terraform
echo "📦 Initializing Terraform..."
terraform init


# Create Terraform plan with OIDC provider ID
echo "📝 Creating Terraform plan..."
terraform plan -out=tfplan -var="stage=$STAGE"

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

# Get OIDC provider ID from EKS cluster
echo "🔍 Getting OIDC provider ID from EKS cluster..."
OIDC_PROVIDER_ID=$(aws eks describe-cluster --name "$EKS_CLUSTER" --region "$AWS_REGION" --query "cluster.identity.oidc.issuer" --output text | sed 's|https://oidc.eks.us-east-1.amazonaws.com/id/||')

if [ -z "$OIDC_PROVIDER_ID" ]; then
    echo "❌ Failed to get OIDC provider ID from EKS cluster."
    exit 1
fi

echo "✅ Got OIDC provider ID: $OIDC_PROVIDER_ID"

# Wait for EKS cluster to be ready
echo "⏳ Waiting for EKS cluster to be ready..."
aws eks wait cluster-active --name "$EKS_CLUSTER" --region "$AWS_REGION"

# Update kubeconfig
echo "🔧 Updating kubeconfig..."
aws eks update-kubeconfig --name "$EKS_CLUSTER" --region "$AWS_REGION"

# Create namespace
echo "📁 Creating namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
