#!/bin/bash

# Setup Application Infrastructure for Research Report Generation System
# Creates: Resource Group, ACR, Container Apps Environment, File Share

set -e

# Configuration
APP_RESOURCE_GROUP="research-report-app-rg"
LOCATION="eastus"
APP_ACR_NAME="researchreportacr"
CONTAINER_ENV="research-report-env"
# Generate unique storage account name (max 24 chars, lowercase, alphanumeric only)
STORAGE_ACCOUNT="reportapp$(date +%s | tail -c 7)"
FILE_SHARE="generated-reports"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Setting up Application Infrastructure                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Create Resource Group
echo "Creating App Resource Group: $APP_RESOURCE_GROUP..."
az group create --name $APP_RESOURCE_GROUP --location $LOCATION