HelixMind Terraform infra (starter)

This folder contains a starter Terraform scaffold for deploying the HelixMind app to AWS.

What's included
- main.tf: core resources (S3 + CloudFront for frontend, ECR, ECS Fargate, ALB, SQS, Secrets Manager)
- variables.tf: variables used by the config
- outputs.tf: useful outputs such as ALB DNS and bucket name
- backend.tf: commented example of an S3 backend config (bootstrap required)

Bootstrap remote state
1. Create S3 bucket and DynamoDB table for state locking (one-time operation):
   aws s3api create-bucket --bucket my-terraform-states-yourorg --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1
   aws dynamodb create-table --table-name terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
2. Update `infra/backend.tf` by uncommenting and setting your bucket and table names.
3. Run `terraform init` then `terraform plan` and `terraform apply` in the `infra/` directory.

Notes & next steps
- This is a starting point. You should:
  - Replace the default secret value in Secrets Manager with a secure value (use CI to inject secrets, not Terraform state).
  - Configure proper Security Groups in place of the empty `security_groups = []` placeholders.
  - Wire CI (GitHub Actions) to build images, push to ECR, and call Terraform apply (or use an infra pipeline).
  - Replace `cloudfront_default_certificate` with an ACM certificate ARN for production (and use Route53 DNS validation).
  - Consider splitting resources into modules (network, ecs, s3-website, ecr, sqs, secrets) for maintainability.

If you want, I can now:
- Break this scaffold into reusable modules and create a `dev/` example with minimal inputs.
- Add a GitHub Actions workflow that builds the backend image, publishes to ECR and runs Terraform plan/apply for dev.
