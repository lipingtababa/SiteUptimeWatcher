resource "aws_iam_role" "watcher_pod_role" {
  name = "watcher-pod-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::975688691016:oidc-provider/${local.eks_oidc_provider_url}"
        }
        Condition = {
          StringEquals = {
            "${local.eks_oidc_provider_url}:sub": "system:serviceaccount:watcher:watcher-sa",
            "${local.eks_oidc_provider_url}:aud": "sts.amazonaws.com"
          }
        }
      }
    ]
  })
}

# Add policy for SSM parameter access
resource "aws_iam_policy" "ssm_reader_policy" {
  name        = "ssm-reader-policy"
  description = "Policy to read SSM parameters"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = [
          aws_ssm_parameter.db_host.arn,
          aws_ssm_parameter.db_port.arn,
          aws_ssm_parameter.db_name.arn,
          aws_ssm_parameter.db_user.arn,
          aws_ssm_parameter.db_password.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "watcher_pod_role_ssm_reader" {
  role       = aws_iam_role.watcher_pod_role.name
  policy_arn = aws_iam_policy.ssm_reader_policy.arn
}

resource "aws_iam_role_policy_attachment" "watcher_pod_role_access_s3" {
  role       = aws_iam_role.watcher_pod_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy_attachment" "watcher_pod_role_pull_image" {
  role       = aws_iam_role.watcher_pod_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy" "watcher_pod_policy" {
  name = "watcher-pod-policy"
  role = aws_iam_role.watcher_pod_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ]
        Resource = [
          "arn:aws:ssm:us-east-1:975688691016:parameter/watcher/db/*",
          "arn:aws:ssm:us-east-1:975688691016:parameter/watcher/postgre/*"
        ]
      }
    ]
  })
}

resource "aws_iam_openid_connect_provider" "oidc_idp" {
  url             = local.oidc_provider_url
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["087E8ED1E7951F9ED0E098541DE06F0DA698D309"]
}
