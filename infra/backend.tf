/*
Terraform backend configuration for GenomeGuard

Before using this backend:
1. Create S3 bucket for state storage:
   aws s3api create-bucket --bucket genomeguard-terraform-state-YOUR_ACCOUNT_ID --region us-east-1
   
2. Enable versioning:
   aws s3api put-bucket-versioning --bucket genomeguard-terraform-state-YOUR_ACCOUNT_ID --versioning-configuration Status=Enabled
   
3. Create DynamoDB table for state locking:
   aws dynamodb create-table \
     --table-name genomeguard-terraform-locks \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

4. Update the bucket name below with your account ID
5. Uncomment the backend block and run `terraform init`
*/

# Uncomment and configure after creating the S3 bucket and DynamoDB table
# terraform {
#   backend "s3" {
#     bucket         = "genomeguard-terraform-state-YOUR_ACCOUNT_ID"
#     key            = "genomeguard/terraform.tfstate"
#     region         = "us-east-1"
#     dynamodb_table = "genomeguard-terraform-locks"
#     encrypt        = true
#   }
# }

