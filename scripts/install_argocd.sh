#!/bin/bash
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
fi

# Get ArgoCD admin password
echo "🔑 Retrieving ArgoCD admin password..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
if [ -n "$ARGOCD_PASSWORD" ]; then
    echo "✅ ArgoCD admin credentials:"
    echo "   Username: admin"
    echo "   Password: $ARGOCD_PASSWORD"
else
    echo "⚠️ Could not retrieve ArgoCD admin password. You may need to reset it."
    echo "   Run: kubectl -n argocd patch secret argocd-initial-admin-secret -p '{\"data\":{\"password\":\"'$(openssl rand -base64 24)'\"}}'"
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
cd "$PROJECT_ROOT"
if [ -f "infra/argocd/watcher.yaml" ]; then
    kubectl apply -f infra/argocd/watcher.yaml
    echo "✅ Watcher application deployed successfully!"
else
    echo "⚠️ Watcher application manifest not found at infra/argocd/watcher.yaml"
    echo "Please create the manifest and apply it manually."
fi

echo "✅ Cluster setup completed successfully!"

# Set up port forwarding for ArgoCD UI
if [ -n "$ARGOCD_PORT" ]; then
    echo "🌐 Setting up port forwarding for ArgoCD UI..."
    echo "🔒 Port forwarding will run in the background. Press Ctrl+C to stop it when you're done."
    echo "🌐 ArgoCD UI will be available at: https://localhost:$ARGOCD_PORT"
    
    # Start port forwarding in the background
    nohup kubectl port-forward -n argocd svc/argocd-server $ARGOCD_PORT:443 &
    PF_PID=$!
    
    echo "⏳ Port forwarding started with PID: $PF_PID"
    echo "🔒 To stop port forwarding, run: kill $PF_PID"
else
    echo "⚠️ Could not determine ArgoCD UI URL. You may need to check the service status manually."
    echo "Run: kubectl get svc argocd-server -n argocd"
fi
