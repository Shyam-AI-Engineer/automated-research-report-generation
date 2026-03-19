#!/bin/bash

# Build and Push Docker Image for Research Report Generation System

set -e

# Configuration
APP_ACR_NAME="researchreportacr"
IMAGE_NAME="research-report-app"
TAG="${1:-latest}"

echo "Building Docker image for Research Report Generation System..."
echo "Tag: $TAG"
echo ""