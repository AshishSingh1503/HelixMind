output "frontend_bucket" {
  description = "S3 bucket for frontend"
  value       = aws_s3_bucket.frontend_bucket.id
}

output "cloudfront_domain" {
  description = "CloudFront domain for frontend"
  value       = aws_cloudfront_distribution.frontend_cdn.domain_name
}

output "ecr_repo" {
  description = "ECR repository URL for backend"
  value       = aws_ecr_repository.backend_repo.repository_url
}

output "alb_dns" {
  description = "ALB DNS name for backend service"
  value       = aws_lb.alb.dns_name
}

output "sqs_queue_url" {
  description = "SQS queue URL for analysis"
  value       = aws_sqs_queue.analysis_queue.id
}
