# GenomeGuard Terraform Variables
aws_region   = "us-east-1"
env          = "dev"
project_name = "genomeguard"

# S3 Bucket Names (globally unique)
frontend_bucket_name = "genomeguard-frontend-dev-731787353717"
uploads_bucket_name  = "genomeguard-uploads-dev-731787353717"

# Container Images (using nginx as placeholder until Docker is available)
backend_image = "nginx:latest"
worker_image  = "nginx:latest"

# ECS Configuration
backend_desired_count = 1
backend_cpu          = 512
backend_memory       = 1024
worker_cpu           = 1024
worker_memory        = 2048

# DocumentDB Configuration
docdb_username       = "genomeguard"
docdb_password       = "GenomeGuard2024!SecurePass"
docdb_instance_class = "db.t3.medium"
docdb_instance_count = 1

# Security
jwt_secret = "super-secure-jwt-secret-key-for-genomeguard-2024"

# Logging
log_retention_days = 14

# Tags
tags = {
  Project     = "GenomeGuard"
  Environment = "dev"
  ManagedBy   = "Terraform"
}