resource "aws_iam_role" "datakit_role" {
  name = "datakit-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.this.arn
        }
        Condition = {
          StringEquals = {
            "${aws_iam_openid_connect_provider.this.url}:sub" = "system:serviceaccount:watcher:watcher-sa"
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "datakit_policy" {
  name = "datakit-policy"
  role = aws_iam_role.datakit_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:us-east-1:975688691016:parameter/watcher/*"
        ]
      }
    ]
  })
} 