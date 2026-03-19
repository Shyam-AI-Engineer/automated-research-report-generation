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

# Create Storage Account for Reports
echo "Creating Storage Account: $STORAGE_ACCOUNT..."
az storage account create \
  --resource-group $APP_RESOURCE_GROUP \
  --name $STORAGE_ACCOUNT \
  --location $LOCATION \
  --sku Standard_LRS

# Get Storage Account Key
STORAGE_KEY=$(az storage account keys list \
  --resource-group $APP_RESOURCE_GROUP \
  --account-name $STORAGE_ACCOUNT \
  --query '[0].value' -o tsv)

# Create File Share for Reports
echo "Creating File Share: $FILE_SHARE..."
az storage share create \
  --name $FILE_SHARE \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY