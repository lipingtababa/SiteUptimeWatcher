#!/bin/bash
set -e

# Set AWS account ID
export AWS_ACCOUNT="975688691016"
export AWS_REGION="us-east-1"
export EKS_CLUSTER="idp"
export NAMESPACE="watcher"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying applications...${NC}"

# Apply DataKit resources
echo -e "${YELLOW}Applying DataKit resources...${NC}"
kubectl apply -k ../infra/application/datakit

# Apply watcher application resources
echo -e "${YELLOW}Applying watcher application resources...${NC}"
kubectl apply -k ../infra/application

# Wait for resources to be ready
echo -e "${YELLOW}Waiting for resources to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/watcher -n $NAMESPACE

# Check application status
echo -e "${YELLOW}Checking application status...${NC}"
kubectl get pods -n $NAMESPACE
kubectl get svc -n $NAMESPACE

echo -e "${GREEN}Applications deployed successfully!${NC}" 