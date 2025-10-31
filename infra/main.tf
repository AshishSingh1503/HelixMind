/*
Terraform starter for HelixMind (dev-friendly, production-minded)

This file provisions:
- S3 bucket for frontend + CloudFront distribution
- ECR repository for backend images
- ECS Fargate cluster + task definition + service (behind an ALB)
- ALB (public) and target group
- SQS queue for background processing
- Secrets Manager secret placeholder for app secrets

Notes:
- This is a scaffold. You must build and push container images separately (CI). The ECS TaskDefinition references a variable `backend_image` which you should set via CI or terraform var.
- Backend state locking: configure `infra/backend.tf` with an S3 backend/dynamo table (or bootstrap the bucket/DynamoDB table manually first).
- Adjust sizes, CPU/memory, scaling, and VPC/subnet selection to match your environment.
*/

terraform {
  required_version = ">= 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ------------------------------
# Networking (basic) - use default VPC by default
# ------------------------------
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Public subnets (for ALB) and private subnets (for ECS tasks)
locals {
  public_subnets  = [for s in data.aws_subnets.default.ids : s][0:2]
  private_subnets = [for s in data.aws_subnets.default.ids : s][2:4] != [] ? [for s in data.aws_subnets.default.ids : s][2:4] : [for s in data.aws_subnets.default.ids : s][0:2]
}

# ------------------------------
# S3 bucket for frontend
# ------------------------------
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = var.frontend_bucket_name
  acl    = "private"

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  tags = var.tags
}

resource "aws_s3_bucket_public_access_block" "frontend_block" {
  bucket = aws_s3_bucket.frontend_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CloudFront distribution for static site
resource "aws_cloudfront_origin_access_identity" "oai" {
  comment = "OAI for HelixMind frontend"
}

resource "aws_cloudfront_distribution" "frontend_cdn" {
  enabled = true

  origins {
    origin_id   = "s3-frontend"
    domain_name = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.oai.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "s3-frontend"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  tags = var.tags
}

# ------------------------------
# ECR for backend
# ------------------------------
resource "aws_ecr_repository" "backend_repo" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"

  tags = var.tags
}

# ------------------------------
# IAM roles for ECS
# ------------------------------
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-exec-role-${var.env}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Minimal task role for app to access S3, SQS and Secrets Manager
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role-${var.env}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

resource "aws_iam_policy" "app_policy" {
  name = "${var.project_name}-app-policy-${var.env}"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Effect = "Allow", Action = ["s3:PutObject","s3:GetObject","s3:DeleteObject"], Resource = "${aws_s3_bucket.frontend_bucket.arn}/*" },
      { Effect = "Allow", Action = ["sqs:SendMessage","sqs:ReceiveMessage","sqs:DeleteMessage","sqs:GetQueueAttributes"], Resource = "*" },
      { Effect = "Allow", Action = ["secretsmanager:GetSecretValue","secretsmanager:DescribeSecret"], Resource = "*" }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_policy_attach" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.app_policy.arn
}

# ------------------------------
# ECS Cluster + Service + ALB
# ------------------------------
resource "aws_ecs_cluster" "cluster" {
  name = "${var.project_name}-cluster-${var.env}"
}

resource "aws_lb" "alb" {
  name               = "${var.project_name}-alb-${var.env}"
  internal           = false
  load_balancer_type = "application"
  subnets            = local.public_subnets
  security_groups    = []
  tags = var.tags
}

resource "aws_lb_target_group" "tg" {
  name     = "${var.project_name}-tg-${var.env}"
  port     = var.container_port
  protocol = "HTTP"
  vpc_id   = data.aws_vpc.default.id
  health_check {
    path                = "/health"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

resource "aws_ecs_task_definition" "task" {
  family                   = "${var.project_name}-task-${var.env}"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "backend",
      image     = var.backend_image,
      essential = true,
      portMappings = [ { containerPort = var.container_port, hostPort = var.container_port, protocol = "tcp" } ],
      environment = [ { name = "ENV", value = var.env } ],
      logConfiguration = { logDriver = "awslogs", options = { "awslogs-group" = "/ecs/${var.project_name}", "awslogs-region" = var.aws_region, "awslogs-stream-prefix" = "backend" } }
    }
  ])
}

resource "aws_ecs_service" "service" {
  name            = "${var.project_name}-service-${var.env}"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = var.service_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = local.private_subnets
    assign_public_ip = false
    security_groups  = []
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name   = "backend"
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.http]
}

# ------------------------------
# SQS (background queue)
# ------------------------------
resource "aws_sqs_queue" "analysis_queue" {
  name = "${var.project_name}-analysis-queue-${var.env}"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 86400
  tags = var.tags
}

# ------------------------------
# Secrets Manager placeholder
# ------------------------------
resource "aws_secretsmanager_secret" "app_secret" {
  name = "${var.project_name}/app-secret-${var.env}"
  description = "Application secrets for HelixMind ${var.env}"
  tags = var.tags
}

# Example secret value (do not store secrets in tfstate in production). Prefer external secret creation or use CI to push secret values.
resource "aws_secretsmanager_secret_version" "app_secret_value" {
  secret_id     = aws_secretsmanager_secret.app_secret.id
  secret_string = jsonencode({ JWT_SECRET = "REPLACE_ME_WITH_SECURE_VALUE" })
}

# ------------------------------
# CloudWatch Log Group for ECS
# ------------------------------
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 14
}

# ------------------------------
# Outputs
# ------------------------------
output "frontend_bucket" {
  value = aws_s3_bucket.frontend_bucket.id
}

output "cloudfront_domain" {
  value = aws_cloudfront_distribution.frontend_cdn.domain_name
}

output "ecr_repo" {
  value = aws_ecr_repository.backend_repo.repository_url
}

output "alb_dns" {
  value = aws_lb.alb.dns_name
}

output "sqs_queue_url" {
  value = aws_sqs_queue.analysis_queue.id
}
