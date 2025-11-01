#!/bin/bash

# GenomeGuard One-Time Deployment Script
# Complete deployment of GenomeGuard infrastructure to AWS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION=${AWS_REGION:-us-east-1}
ENV=${ENV:-dev}
PROJECT_NAME="genomeguard"

echo -e "${GREEN}🧬 GenomeGuard AWS Deployment Script${NC}"
echo "=================================="

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed${NC}"
    exit 1
fi

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform is not installed${NC}"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: $AWS_ACCOUNT_ID"

# Function to create S3 backend bucket
create_backend_bucket() {
    local bucket_name="genomeguard-terraform-state-$AWS_ACCOUNT_ID"
    
    echo -e "${YELLOW}Creating Terraform backend S3 bucket...${NC}"
    
    if aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
        echo -e "${GREEN}✅ S3 bucket $bucket_name already exists${NC}"
    else
        aws s3api create-bucket --bucket "$bucket_name" --region "$AWS_REGION"
        aws s3api put-bucket-versioning --bucket "$bucket_name" --versioning-configuration Status=Enabled
        aws s3api put-bucket-encryption --bucket "$bucket_name" --server-side-encryption-configuration '{
            "Rules": [
                {
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }
            ]
        }'
        echo -e "${GREEN}✅ Created S3 bucket $bucket_name${NC}"
    fi
}

# Function to create DynamoDB table for state locking
create_dynamodb_table() {
    local table_name="genomeguard-terraform-locks"
    
    echo -e "${YELLOW}Creating DynamoDB table for state locking...${NC}"
    
    if aws dynamodb describe-table --table-name "$table_name" &>/dev/null; then
        echo -e "${GREEN}✅ DynamoDB table $table_name already exists${NC}"
    else
        aws dynamodb create-table \
            --table-name "$table_name" \
            --attribute-definitions AttributeName=LockID,AttributeType=S \
            --key-schema AttributeName=LockID,KeyType=HASH \
            --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
            --region "$AWS_REGION"
        
        echo -e "${YELLOW}Waiting for DynamoDB table to be active...${NC}"
        aws dynamodb wait table-exists --table-name "$table_name"
        echo -e "${GREEN}✅ Created DynamoDB table $table_name${NC}"
    fi
}

# Function to create ECR repositories
create_ecr_repos() {
    echo -e "${YELLOW}Creating ECR repositories...${NC}"
    
    for repo in "backend" "worker"; do
        local repo_name="$PROJECT_NAME-$repo"
        
        if aws ecr describe-repositories --repository-names "$repo_name" &>/dev/null; then
            echo -e "${GREEN}✅ ECR repository $repo_name already exists${NC}"
        else
            aws ecr create-repository --repository-name "$repo_name" --region "$AWS_REGION"
            echo -e "${GREEN}✅ Created ECR repository $repo_name${NC}"
        fi
    done
}

# Function to build and push Docker images
build_and_push_images() {
    echo -e "${YELLOW}Building and pushing Docker images...${NC}"
    
    # Get ECR login token
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
    
    # Build and push backend image
    echo -e "${YELLOW}Building backend image...${NC}"
    cd ../
    docker build -t "$PROJECT_NAME-backend" -f Dockerfile .
    docker tag "$PROJECT_NAME-backend:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME-backend:latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME-backend:latest"
    
    # Build and push worker image (same as backend for now)
    docker tag "$PROJECT_NAME-backend:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME-worker:latest"
    docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME-worker:latest"
    
    cd infra/
    echo -e "${GREEN}✅ Docker images built and pushed${NC}"
}

# Function to generate terraform.tfvars
generate_tfvars() {
    echo -e "${YELLOW}Generating terraform.tfvars...${NC}"
    
    if [ ! -f "terraform.tfvars" ]; then
        cat > terraform.tfvars << EOF
# GenomeGuard Terraform Variables
aws_region   = "$AWS_REGION"
env          = "$ENV"
project_name = "$PROJECT_NAME"

# S3 Bucket Names (globally unique)
frontend_bucket_name = "$PROJECT_NAME-frontend-$ENV-$AWS_ACCOUNT_ID"
uploads_bucket_name  = "$PROJECT_NAME-uploads-$ENV-$AWS_ACCOUNT_ID"

# Container Images
backend_image = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME-backend:latest"
worker_image  = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$PROJECT_NAME-worker:latest"

# ECS Configuration
backend_desired_count = 2
backend_cpu          = 512
backend_memory       = 1024
worker_cpu           = 1024
worker_memory        = 2048

# DocumentDB Configuration
docdb_username       = "genomeguard"
docdb_password       = "$(openssl rand -base64 32)"
docdb_instance_class = "db.t3.medium"
docdb_instance_count = 1

# Security
jwt_secret = "$(openssl rand -base64 64)"

# Logging
log_retention_days = 14

# Tags
tags = {
  Project     = "GenomeGuard"
  Environment = "$ENV"
  ManagedBy   = "Terraform"
}
EOF
        echo -e "${GREEN}✅ Generated terraform.tfvars${NC}"
    else
        echo -e "${GREEN}✅ terraform.tfvars already exists${NC}"
    fi
}

# Function to deploy infrastructure
deploy_infrastructure() {
    echo -e "${YELLOW}Deploying infrastructure with Terraform...${NC}"
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -out=tfplan
    
    # Apply deployment
    echo -e "${YELLOW}Applying Terraform plan...${NC}"
    terraform apply tfplan
    
    echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"
}

# Function to build and deploy frontend
deploy_frontend() {
    echo -e "${YELLOW}Building and deploying frontend...${NC}"
    
    # Get frontend bucket name from Terraform output
    FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)
    CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)
    
    # Build React app
    cd ../web
    npm install
    npm run build
    
    # Upload to S3
    aws s3 sync build/ "s3://$FRONTEND_BUCKET" --delete
    
    # Invalidate CloudFront cache
    aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_ID" --paths "/*"
    
    cd ../infra
    echo -e "${GREEN}✅ Frontend deployed successfully${NC}"
}

# Main deployment flow
main() {
    echo -e "${YELLOW}Starting GenomeGuard deployment...${NC}"
    
    # Step 1: Create backend infrastructure
    create_backend_bucket
    create_dynamodb_table
    
    # Step 2: Create ECR repositories
    create_ecr_repos
    
    # Step 3: Build and push Docker images
    build_and_push_images
    
    # Step 4: Generate Terraform variables
    generate_tfvars
    
    # Step 5: Deploy infrastructure
    deploy_infrastructure
    
    # Step 6: Deploy frontend
    deploy_frontend
    
    echo -e "${GREEN}🎉 GenomeGuard deployment completed successfully!${NC}"
    echo ""
    echo "Application URLs:"
    echo "Frontend: $(terraform output -raw application_url)"
    echo "API: $(terraform output -raw api_url)"
    echo ""
    echo "Next steps:"
    echo "1. Test the application endpoints"
    echo "2. Upload sample VCF files"
    echo "3. Monitor CloudWatch logs"
    echo "4. Configure custom domain if needed"
}

# Run main function
main "$@"