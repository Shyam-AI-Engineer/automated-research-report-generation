#!/bin/bash

# Azure Deployment Script for Jenkins
# Deploys Jenkins with Python 3.11 and Azure CLI for Research Report Generation CI/CD

set -e

# Configuration
RESOURCE_GROUP="research-report-jenkins-rg"
LOCATION="eastus"
STORAGE_ACCOUNT="reportjenkinsstore"
FILE_SHARE="jenkins-data"
ACR_NAME="reportjenkinsacr"
CONTAINER_NAME="jenkins-research-report"
DNS_NAME_LABEL="jenkins-research-$(date +%s | tail -c 6)"
JENKINS_IMAGE_NAME="custom-jenkins"
JENKINS_IMAGE_TAG="lts-git-configured"

# Subscription ID - can be passed as argument or environment variable
SUBSCRIPTION_ID="${1:-${AZURE_SUBSCRIPTION_ID}}"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Deploying Jenkins for Research Report Generation     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Verify Azure login
echo "Verifying Azure login..."
if ! az account show &>/dev/null; then
    echo "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

# Set subscription if provided
if [ -n "$SUBSCRIPTION_ID" ]; then
    echo "Setting Azure subscription to: $SUBSCRIPTION_ID"
    az account set --subscription "$SUBSCRIPTION_ID"
    if [ $? -ne 0 ]; then
        echo "Failed to set subscription. Please verify the subscription ID."
        exit 1
    fi
else
    echo "ℹ️No subscription ID provided. Using current default subscription."
    CURRENT_SUB=$(az account show --query id -o tsv)
    echo "   Current subscription: $CURRENT_SUB"
fi

# Verify subscription is set correctly
CURRENT_SUB=$(az account show --query id -o tsv)
echo "Using subscription: $CURRENT_SUB"
echo ""

# Store subscription ID for use in commands
if [ -z "$SUBSCRIPTION_ID" ]; then
    SUBSCRIPTION_ID="$CURRENT_SUB"
fi

# Create Resource Group
echo "Creating Resource Group: $RESOURCE_GROUP..."
az group create --name $RESOURCE_GROUP --location $LOCATION --subscription "$SUBSCRIPTION_ID"

# Create Storage Account
echo "Creating Storage Account: $STORAGE_ACCOUNT..."
az storage account create \
  --resource-group $RESOURCE_GROUP \
  --name $STORAGE_ACCOUNT \
  --location $LOCATION \
  --sku Standard_LRS \
  --subscription "$SUBSCRIPTION_ID"

# Get Storage Account Key
STORAGE_KEY=$(az storage account keys list \
  --resource-group $RESOURCE_GROUP \
  --account-name $STORAGE_ACCOUNT \
  --subscription "$SUBSCRIPTION_ID" \
  --query '[0].value' -o tsv)

# Create File Share
echo "Creating File Share: $FILE_SHARE..."
az storage share create \
  --name $FILE_SHARE \
  --account-name $STORAGE_ACCOUNT \
  --account-key $STORAGE_KEY \
  --subscription "$SUBSCRIPTION_ID"

# Create Azure Container Registry
echo "Creating Container Registry: $ACR_NAME..."
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true \
  --subscription "$SUBSCRIPTION_ID"