#!/bin/bash

# Build and deploy GenomeGuard backend to AWS ECS

# Variables
AWS_ACCOUNT_ID="731787353717"
AWS_REGION="us-east-1"
ECR_REPO="genomeguard-backend"
IMAGE_TAG="latest"
CLUSTER_NAME="genomeguard-cluster-dev"
SERVICE_NAME="genomeguard-backend-dev"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build Docker image
cd backend
docker build -t $ECR_REPO:$IMAGE_TAG .

# Tag for ECR
docker tag $ECR_REPO:$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG

# Push to ECR
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:$IMAGE_TAG

# Force new deployment
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment

echo "Backend deployment initiated. Check ECS console for status."