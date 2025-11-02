# Create S3 bucket for source code
$bucketName = "genomeguard-codebuild-source-731787353717"
aws s3 mb s3://$bucketName --region us-east-1

# Create zip of backend code
Compress-Archive -Path "backend\*" -DestinationPath "backend-source.zip" -Force

# Upload to S3
aws s3 cp backend-source.zip s3://$bucketName/backend-source.zip

# Create CodeBuild project
$projectConfig = @"
{
  "name": "genomeguard-backend-build",
  "source": {
    "type": "S3",
    "location": "$bucketName/backend-source.zip"
  },
  "artifacts": {
    "type": "NO_ARTIFACTS"
  },
  "environment": {
    "type": "LINUX_CONTAINER",
    "image": "aws/codebuild/amazonlinux2-x86_64-standard:5.0",
    "computeType": "BUILD_GENERAL1_SMALL",
    "privilegedMode": true,
    "environmentVariables": [
      {
        "name": "AWS_DEFAULT_REGION",
        "value": "us-east-1"
      },
      {
        "name": "AWS_ACCOUNT_ID",
        "value": "731787353717"
      },
      {
        "name": "IMAGE_REPO_NAME",
        "value": "genomeguard-backend"
      },
      {
        "name": "IMAGE_TAG",
        "value": "latest"
      }
    ]
  },
  "serviceRole": "arn:aws:iam::731787353717:role/service-role/codebuild-genomeguard-service-role"
}
"@

# Create the project
$projectConfig | Out-File -FilePath "codebuild-project.json" -Encoding utf8
aws codebuild create-project --cli-input-json file://codebuild-project.json

# Start build
aws codebuild start-build --project-name genomeguard-backend-build