# ------------------------------
# Infrastructure Outputs
# ------------------------------
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

# ------------------------------
# S3 Outputs
# ------------------------------
output "frontend_bucket_name" {
  description = "Name of the S3 bucket for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "uploads_bucket_name" {
  description = "Name of the S3 bucket for uploads"
  value       = aws_s3_bucket.uploads.id
}

# ------------------------------
# CloudFront Outputs
# ------------------------------
output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}

# ------------------------------
# ECR Outputs
# ------------------------------
output "backend_ecr_repository_url" {
  description = "URL of the backend ECR repository"
  value       = aws_ecr_repository.backend.repository_url
}

output "worker_ecr_repository_url" {
  description = "URL of the worker ECR repository"
  value       = aws_ecr_repository.worker.repository_url
}

# ------------------------------
# Load Balancer Outputs
# ------------------------------
output "alb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.alb.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.alb.zone_id
}

# ------------------------------
# ECS Outputs
# ------------------------------
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "backend_service_name" {
  description = "Name of the backend ECS service"
  value       = aws_ecs_service.backend.name
}

# ------------------------------
# DocumentDB Outputs
# ------------------------------
output "docdb_cluster_endpoint" {
  description = "DocumentDB cluster endpoint"
  value       = aws_docdb_cluster.main.endpoint
  sensitive   = true
}

output "docdb_cluster_port" {
  description = "DocumentDB cluster port"
  value       = aws_docdb_cluster.main.port
}

# ------------------------------
# SQS Outputs
# ------------------------------
output "analysis_queue_url" {
  description = "URL of the analysis SQS queue"
  value       = aws_sqs_queue.analysis.id
}

output "analysis_dlq_url" {
  description = "URL of the analysis dead letter queue"
  value       = aws_sqs_queue.analysis_dlq.id
}

# ------------------------------
# Secrets Manager Outputs
# ------------------------------
output "app_secrets_arn" {
  description = "ARN of the application secrets"
  value       = aws_secretsmanager_secret.app_secrets.arn
  sensitive   = true
}

# ------------------------------
# Application URLs
# ------------------------------
output "application_url" {
  description = "Main application URL (CloudFront)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "api_url" {
  description = "API URL (via CloudFront)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}/api"
}
