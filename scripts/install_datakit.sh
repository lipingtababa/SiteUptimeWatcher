#!/bin/bash

# Exit on error
set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installing DataKit using Helm...${NC}"

# Add the DataKit Helm repository
echo -e "${YELLOW}Adding DataKit Helm repository...${NC}"
helm repo add datakit https://pubrepo.guance.com/chartrepo/datakit
helm repo update

# Install DataKit
echo -e "${YELLOW}Installing DataKit...${NC}"
helm install datakit datakit/datakit \
  --namespace datakit \
  --create-namespace \
  --set datakit.dataway_url="https://eu1-openway.truewatch.com?token=tkn_79e8251c3aac427fb3a641822356473e"

echo -e "${GREEN}DataKit installation completed!${NC}" 