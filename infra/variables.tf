# ------------------------------
# General Variables
# ------------------------------
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "env" {
  description = "Environment (dev/stage/prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "stage", "prod"], var.env)
    error_message = "Environment must be dev, stage, or prod."
  }
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "genomeguard"
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project   = "GenomeGuard"
    ManagedBy = "Terraform"
  }
}

# ------------------------------
# Networking Variables
# ------------------------------
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# ------------------------------
# S3 Variables
# ------------------------------
variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend (must be globally unique)"
  type        = string
}

variable "uploads_bucket_name" {
  description = "S3 bucket name for VCF uploads (must be globally unique)"
  type        = string
}

# ------------------------------
# Container Variables
# ------------------------------
variable "backend_image" {
  description = "Backend container image URI (ECR)"
  type        = string
  default     = "nginx:latest"  # Placeholder
}

variable "worker_image" {
  description = "Worker container image URI (ECR)"
  type        = string
  default     = "nginx:latest"  # Placeholder
}

variable "container_port" {
  description = "Container port exposed by the backend"
  type        = number
  default     = 8000
}

# ------------------------------
# ECS Variables
# ------------------------------
variable "backend_cpu" {
  description = "CPU units for backend task"
  type        = number
  default     = 512
}

variable "backend_memory" {
  description = "Memory (MB) for backend task"
  type        = number
  default     = 1024
}

variable "backend_desired_count" {
  description = "Desired number of backend tasks"
  type        = number
  default     = 2
}

variable "worker_cpu" {
  description = "CPU units for worker task"
  type        = number
  default     = 1024
}

variable "worker_memory" {
  description = "Memory (MB) for worker task"
  type        = number
  default     = 2048
}

# ------------------------------
# DocumentDB Variables
# ------------------------------
variable "docdb_username" {
  description = "DocumentDB master username"
  type        = string
  default     = "genomeguard"
}

variable "docdb_password" {
  description = "DocumentDB master password"
  type        = string
  sensitive   = true
}

variable "docdb_instance_class" {
  description = "DocumentDB instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "docdb_instance_count" {
  description = "Number of DocumentDB instances"
  type        = number
  default     = 1
}

# ------------------------------
# Security Variables
# ------------------------------
variable "jwt_secret" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

# ------------------------------
# Logging Variables
# ------------------------------
variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 14
}
