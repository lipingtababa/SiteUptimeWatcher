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

resource "aws_secretsmanager_secret" "default" {
  name = "/watcher/postgre/password"
  tags = {
    Environment = "production"
    Project     = "watcher"
  }
}

resource "aws_iam_policy" "secret_reader_policy" {
  name = "secret_reader_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Effect = "Allow"
        Resource = [
          aws_secretsmanager_secret.default.arn
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "secret_writer_policy" {
  name = "secret_writer_policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:PutSecretValue"
        ]
        Effect = "Allow"
        Resource = [
          aws_secretsmanager_secret.default.arn
        ]
      }
    ]
  })
}
