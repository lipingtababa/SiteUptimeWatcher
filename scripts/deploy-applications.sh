#!/bin/bash
set -e

# Set AWS account ID
export NAMESPACE="watcher"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying applications...${NC}"

# Apply watcher application resources directly
echo -e "${YELLOW}Applying watcher application resources...${NC}"
kubectl apply -f ../infra/application/watcher.deployment.yaml

# Wait for resources to be ready
echo -e "${YELLOW}Waiting for resources to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/watcher -n $NAMESPACE

# Check application status
echo -e "${YELLOW}Checking application status...${NC}"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE

echo -e "${GREEN}Applications deployed successfully!${NC}" 