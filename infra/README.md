# GenomeGuard AWS Infrastructure

This directory contains Terraform configurations to deploy GenomeGuard to AWS with a production-ready architecture.

## Architecture Overview

```
User → CloudFront → ALB → ECS Fargate (FastAPI)
  ↳ Static site from S3 (CloudFront)
Backend → S3 (uploads)
Backend → DocumentDB (MongoDB compatible)
Backend → SQS → Worker ECS Task → S3/DB
CI → ECR → ECS deployment
```

## Infrastructure Components

### Networking
- **VPC**: Custom VPC with public and private subnets across 2 AZs
- **NAT Gateways**: For private subnet internet access
- **Security Groups**: Properly configured for each service

### Compute
- **ECS Fargate**: Serverless containers for backend and worker
- **Application Load Balancer**: For high availability and SSL termination
- **Auto Scaling**: Based on CPU and memory utilization

### Storage
- **S3 Buckets**: 
  - Frontend static assets
  - VCF file uploads with lifecycle policies
- **DocumentDB**: MongoDB-compatible database cluster

### Messaging
- **SQS**: Analysis queue with dead letter queue
- **CloudWatch**: Comprehensive logging and monitoring

### Security
- **Secrets Manager**: Secure storage of database credentials and JWT secrets
- **IAM Roles**: Least privilege access for all services
- **VPC Security**: Private subnets for sensitive workloads

### CDN & Caching
- **CloudFront**: Global content delivery with API routing
- **S3 Origin Access Identity**: Secure S3 access

## Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Terraform** >= 1.2.0
3. **Docker** for building container images
4. **Node.js** >= 18 for frontend builds

## Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh
```

This script will:
- Create S3 backend bucket and DynamoDB table
- Build and push Docker images to ECR
- Generate terraform.tfvars with secure defaults
- Deploy infrastructure with Terraform
- Build and deploy the frontend

### Option 2: Manual Deployment

#### Step 1: Setup Terraform Backend

```bash
# Get your AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create S3 bucket for Terraform state
aws s3api create-bucket --bucket genomeguard-terraform-state-$AWS_ACCOUNT_ID --region us-east-1
aws s3api put-bucket-versioning --bucket genomeguard-terraform-state-$AWS_ACCOUNT_ID --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name genomeguard-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

#### Step 2: Configure Backend

Uncomment and update the backend configuration in `backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "genomeguard-terraform-state-YOUR_ACCOUNT_ID"
    key            = "genomeguard/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "genomeguard-terraform-locks"
    encrypt        = true
  }
}
```

#### Step 3: Create ECR Repositories

```bash
aws ecr create-repository --repository-name genomeguard-backend
aws ecr create-repository --repository-name genomeguard-worker
```

#### Step 4: Build and Push Images

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend image
cd ../
docker build -t genomeguard-backend .
docker tag genomeguard-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/genomeguard-backend:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/genomeguard-backend:latest

# Tag and push worker image (same as backend for now)
docker tag genomeguard-backend:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/genomeguard-worker:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/genomeguard-worker:latest
```

#### Step 5: Configure Variables

```bash
# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
vim terraform.tfvars
```

Required variables:
- `frontend_bucket_name`: Globally unique S3 bucket name
- `uploads_bucket_name`: Globally unique S3 bucket name
- `backend_image`: ECR image URI
- `worker_image`: ECR image URI
- `docdb_password`: Secure database password
- `jwt_secret`: Secure JWT secret key

#### Step 6: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply deployment
terraform apply
```

#### Step 7: Deploy Frontend

```bash
# Get outputs
FRONTEND_BUCKET=$(terraform output -raw frontend_bucket_name)
CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id)

# Build and deploy frontend
cd ../web
npm install
npm run build
aws s3 sync build/ s3://$FRONTEND_BUCKET --delete
aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_ID --paths "/*"
```

## CI/CD Pipeline

The project includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that:

1. **Tests**: Runs Python and JavaScript tests
2. **Builds**: Creates Docker images and pushes to ECR
3. **Deploys**: Updates infrastructure and deploys frontend

### Required GitHub Secrets

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
DOCDB_PASSWORD=secure_database_password
JWT_SECRET=secure_jwt_secret_key
```

### Deployment Environments

- **develop branch**: Deploys to `dev` environment
- **main branch**: Deploys to `prod` environment

## Configuration

### Environment Variables

The application uses these environment variables:

```bash
# Application
ENV=dev|prod
AWS_DEFAULT_REGION=us-east-1

# Storage
S3_UPLOADS_BUCKET=genomeguard-uploads-dev-123456789

# Database
DOCDB_ENDPOINT=genomeguard-docdb-dev.cluster-xyz.docdb.us-east-1.amazonaws.com
DOCDB_USERNAME=genomeguard
DOCDB_PASSWORD=from_secrets_manager

# Queue
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789/genomeguard-analysis-dev

# Security
JWT_SECRET=from_secrets_manager
```

### Scaling Configuration

#### Development Environment
- Backend: 2 tasks, 512 CPU, 1GB memory
- Worker: On-demand via SQS
- DocumentDB: 1 instance, db.t3.medium

#### Production Environment
- Backend: 3+ tasks, 1024 CPU, 2GB memory
- Worker: Auto-scaling based on queue depth
- DocumentDB: 2+ instances, db.r5.large

## Monitoring and Logging

### CloudWatch Logs
- Backend logs: `/ecs/genomeguard-backend-{env}`
- Worker logs: `/ecs/genomeguard-worker-{env}`

### Metrics
- ECS service metrics
- ALB target group health
- DocumentDB performance
- SQS queue depth

### Alarms
- High CPU/Memory usage
- Failed health checks
- Queue processing delays
- Database connection issues

## Security Best Practices

### Network Security
- Private subnets for all compute resources
- Security groups with minimal required access
- VPC endpoints for AWS services (optional)

### Data Security
- Encryption at rest for all storage
- Encryption in transit (HTTPS/TLS)
- Secrets stored in AWS Secrets Manager
- IAM roles with least privilege

### Application Security
- JWT-based authentication
- Input validation and sanitization
- Rate limiting (via ALB)
- CORS configuration

## Backup and Disaster Recovery

### DocumentDB
- Automated backups (7-day retention)
- Point-in-time recovery
- Cross-region snapshots (production)

### S3
- Versioning enabled
- Cross-region replication (production)
- Lifecycle policies for cost optimization

## Cost Optimization

### Development
- Single AZ deployment
- Smaller instance sizes
- Shorter log retention
- Lifecycle policies for uploads

### Production
- Multi-AZ for high availability
- Reserved instances for predictable workloads
- CloudWatch cost monitoring
- S3 Intelligent Tiering

## Troubleshooting

### Common Issues

1. **ECR Authentication**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   ```

2. **Terraform State Lock**
   ```bash
   terraform force-unlock LOCK_ID
   ```

3. **ECS Task Failures**
   ```bash
   aws ecs describe-tasks --cluster genomeguard-cluster-dev --tasks TASK_ARN
   ```

4. **DocumentDB Connection**
   ```bash
   # Test from ECS task
   mongo --host genomeguard-docdb-dev.cluster-xyz.docdb.us-east-1.amazonaws.com:27017
   ```

### Useful Commands

```bash
# View Terraform outputs
terraform output

# Check ECS service status
aws ecs describe-services --cluster genomeguard-cluster-dev --services genomeguard-backend-dev

# View CloudWatch logs
aws logs tail /ecs/genomeguard-backend-dev --follow

# Check SQS queue
aws sqs get-queue-attributes --queue-url $(terraform output -raw analysis_queue_url) --attribute-names All
```

## Cleanup

To destroy the infrastructure:

```bash
# Destroy Terraform resources
terraform destroy

# Clean up ECR repositories
aws ecr delete-repository --repository-name genomeguard-backend --force
aws ecr delete-repository --repository-name genomeguard-worker --force

# Clean up backend resources (optional)
aws s3 rb s3://genomeguard-terraform-state-$AWS_ACCOUNT_ID --force
aws dynamodb delete-table --table-name genomeguard-terraform-locks
```

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review CloudWatch logs
3. Open a GitHub issue
4. Contact the development team