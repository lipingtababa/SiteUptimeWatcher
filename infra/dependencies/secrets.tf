provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_account" {
  type    = string
  default = "954976318202"
}

# SSM Parameter for PostgreSQL password
resource "aws_ssm_parameter" "postgres_password" {
  name  = "/watcher/postgre/password"
  type  = "SecureString"
  value = "placeholder" # This will be updated by the application
  tags = {
    Environment = "production"
    Project     = "watcher"
  }
}

# SSM Parameter for ArgoCD admin password
resource "aws_ssm_parameter" "argocd_password" {
  name  = "/watcher/argocd/admin-password"
  type  = "SecureString"
  value = "placeholder" # This will be updated during cluster setup
  tags = {
    Environment = "production"
    Project     = "watcher"
  }
}

# IAM policy for reading SSM parameters
resource "aws_iam_policy" "ssm_reader_policy" {
  name = "ssm_reader_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Effect = "Allow"
        Resource = [
          aws_ssm_parameter.postgres_password.arn,
          aws_ssm_parameter.argocd_password.arn
        ]
      }
    ]
  })
}

# IAM policy for writing SSM parameters
resource "aws_iam_policy" "ssm_writer_policy" {
  name = "ssm_writer_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssm:PutParameter"
        ]
        Effect = "Allow"
        Resource = [
          aws_ssm_parameter.postgres_password.arn,
          aws_ssm_parameter.argocd_password.arn
        ]
      }
    ]
  })
}
