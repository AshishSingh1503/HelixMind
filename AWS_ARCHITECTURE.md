# 🏗️ GenomeGuard AWS Infrastructure Architecture

## 📊 Architecture Overview

```
Internet → CloudFront → ALB → ECS Fargate → DocumentDB
    ↓           ↓        ↓         ↓           ↓
   Users    S3 Static   API    Containers   Database
            Frontend   Gateway
```

## 🌐 **Network Layer**
- **VPC**: `vpc-062ac4d0296864938` (us-east-1)
- **Public Subnets**: 
  - `subnet-0283ad8f4ac97d045` (us-east-1a)
  - `subnet-06357e7c5a6a06f80` (us-east-1b)
- **Private Subnets**:
  - `subnet-067e515d80dd81ba7` (us-east-1a) 
  - `subnet-08c38b762a461e6b0` (us-east-1b)

## 🎯 **Frontend Layer**
- **S3 Bucket**: `genomeguard-frontend-dev-731787353717`
- **CloudFront**: `E6VNFZZAXIK46`
- **Domain**: `d1tbs95iqbrmzy.cloudfront.net`
- **Purpose**: Static React app hosting with global CDN

## ⚖️ **Load Balancing**
- **ALB**: `genomeguard-alb-dev-1148343314.us-east-1.elb.amazonaws.com`
- **Zone ID**: `Z35SXDOTRQ7X7K`
- **Target Groups**: Backend services on port 80
- **Health Checks**: `/health` endpoint

## 🐳 **Container Layer**
- **ECS Cluster**: `genomeguard-cluster-dev`
- **Service**: `genomeguard-backend-dev`
- **Launch Type**: Fargate (serverless)
- **ECR Repositories**:
  - Backend: `731787353717.dkr.ecr.us-east-1.amazonaws.com/genomeguard-backend`
  - Worker: `731787353717.dkr.ecr.us-east-1.amazonaws.com/genomeguard-worker`

## 🗄️ **Database Layer**
- **DocumentDB Cluster**: `genomeguard-docdb-dev.cluster-cu1ecmgqonbx.us-east-1.docdb.amazonaws.com`
- **Port**: 27017
- **Engine**: MongoDB-compatible
- **Deployment**: Multi-AZ for high availability

## 📦 **Storage Layer**
- **Frontend Bucket**: `genomeguard-frontend-dev-731787353717`
- **Uploads Bucket**: `genomeguard-uploads-dev-731787353717`
- **Purpose**: Static assets + user file uploads

## 📬 **Message Queue**
- **Analysis Queue**: `genomeguard-analysis-dev`
- **Dead Letter Queue**: `genomeguard-analysis-dlq-dev`
- **Purpose**: Async genomic data processing

## 🔐 **Security Layer**
- **Secrets Manager**: `genomeguard/app-secrets-dev-N325Tr`
- **IAM Roles**: ECS execution + task roles
- **Security Groups**: Network access control
- **Encryption**: At rest and in transit

## 🔧 **DevOps Layer**
- **CodeBuild**: `genomeguard-backend-build`
- **ECR**: Container image registry
- **Terraform**: Infrastructure as Code
- **Auto-deployment**: CI/CD pipeline

## 📈 **Resource Summary**

| Service | Resource ID | Purpose |
|---------|-------------|---------|
| **VPC** | vpc-062ac4d0296864938 | Network isolation |
| **CloudFront** | E6VNFZZAXIK46 | Global CDN |
| **ALB** | genomeguard-alb-dev-* | Load balancing |
| **ECS** | genomeguard-cluster-dev | Container orchestration |
| **DocumentDB** | genomeguard-docdb-dev | MongoDB database |
| **S3** | genomeguard-*-dev-* | Static/file storage |
| **SQS** | genomeguard-analysis-* | Message queuing |
| **ECR** | genomeguard-backend/worker | Container registry |

## 🌍 **Data Flow**

1. **User Request** → CloudFront CDN
2. **Static Assets** → S3 Frontend Bucket
3. **API Calls** → ALB → ECS Fargate
4. **File Uploads** → S3 Uploads Bucket
5. **Processing Jobs** → SQS → Worker Containers
6. **Data Storage** → DocumentDB Cluster
7. **Secrets** → AWS Secrets Manager

## 🔒 **Security Architecture**

- **Network**: Private subnets for backend services
- **Access**: IAM roles with least privilege
- **Encryption**: TLS/SSL for all communications
- **Secrets**: Centralized in AWS Secrets Manager
- **Monitoring**: CloudWatch logs and metrics

## 💰 **Cost Optimization**

- **Fargate**: Pay-per-use containers
- **S3**: Lifecycle policies for storage
- **CloudFront**: Edge caching reduces origin load
- **DocumentDB**: Right-sized instances
- **Auto-scaling**: Based on demand

## 🚀 **Deployment URLs**

- **Frontend**: https://d1tbs95iqbrmzy.cloudfront.net
- **API**: https://d1tbs95iqbrmzy.cloudfront.net/api
- **Direct ALB**: http://genomeguard-alb-dev-1148343314.us-east-1.elb.amazonaws.com

## 📊 **Architecture Benefits**

✅ **Scalable**: Auto-scaling containers  
✅ **Secure**: Private subnets + IAM  
✅ **Reliable**: Multi-AZ deployment  
✅ **Fast**: CloudFront global CDN  
✅ **Cost-effective**: Serverless + managed services  
✅ **Maintainable**: Infrastructure as Code