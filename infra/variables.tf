variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "env" {
  description = "Environment (dev/stage/prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "helixmind"
}

variable "frontend_bucket_name" {
  description = "S3 bucket name for frontend (must be globally unique)"
  type        = string
  default     = "helixmind-frontend-dev-example"
}

variable "backend_image" {
  description = "Backend container image URI (ECR)"
  type        = string
  default     = ""
}

variable "container_port" {
  description = "Container port exposed by the backend"
  type        = number
  default     = 8000
}

variable "task_cpu" {
  type    = number
  default = 512
}

variable "task_memory" {
  type    = number
  default = 1024
}

variable "service_desired_count" {
  type    = number
  default = 1
}

variable "tags" {
  type = map(string)
  default = {
    ManagedBy = "terraform"
    Project   = "helixmind"
  }
}
