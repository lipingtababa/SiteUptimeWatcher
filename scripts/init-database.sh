#!/bin/bash
set -e

# Set namespace
export NAMESPACE="watcher"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Checking database initialization status...${NC}"

# Check if db-init job exists and has completed successfully
if kubectl get job db-init -n $NAMESPACE &> /dev/null; then
  # Check if the job has completed successfully
  if kubectl get job db-init -n $NAMESPACE -o jsonpath='{.status.conditions[?(@.type=="Complete")].status}' | grep -q "True"; then
    echo -e "${GREEN}Database already initialized successfully. Skipping...${NC}"
    exit 0
  else
    # Job exists but hasn't completed successfully, delete it
    echo -e "${YELLOW}Found incomplete db-init job. Deleting it...${NC}"
    kubectl delete job db-init -n $NAMESPACE
  fi
fi

echo -e "${GREEN}Initializing database...${NC}"

# Apply db-init job
echo -e "${YELLOW}Applying db-init job...${NC}"
kubectl apply -f ../infra/application/db-init-job.yaml

# Wait for job to complete
echo -e "${YELLOW}Waiting for db-init job to complete...${NC}"
kubectl wait --for=condition=complete --timeout=300s job/db-init -n $NAMESPACE || {
  echo -e "${RED}Database initialization failed. Checking logs...${NC}"
  kubectl logs -l job-name=db-init -n $NAMESPACE
  exit 1
}

echo -e "${GREEN}Database initialized successfully!${NC}" 