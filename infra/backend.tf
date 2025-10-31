/*
Example backend configuration for Terraform state.

Important: Terraform backend settings must be created/bootstrapped prior to using them.
You can create the S3 bucket and DynamoDB table manually (via AWS Console or AWS CLI) then
uncomment and use this backend block to enable remote state with locking.

Create S3 bucket and DynamoDB table (example AWS CLI commands):
aws s3api create-bucket --bucket my-terraform-states-yourorg --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1
aws dynamodb create-table --table-name terraform-locks --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

Then uncomment the backend block below and run `terraform init`.
*/

/*
terraform {
  backend "s3" {
    bucket         = "my-terraform-states-yourorg"
    key            = "helixmind/${var.env}/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
*/
