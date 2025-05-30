resource "aws_iam_role" "github_action_role" {
  name = "github-action"
  description = "Used by github workflow"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRoleWithWebIdentity"
        Effect = "Allow"
        Principal = {
          Federated = "arn:aws:iam::${var.aws_account}:oidc-provider/token.actions.githubusercontent.com"
        }
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          }
          StringLike = {
            "token.actions.githubusercontent.com:sub" = "repo:lipingtababa/*"
          }
        }
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
        Effect = "Allow"
        Action = [
          "ssm:PutParameter"
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

resource "aws_iam_role_policy_attachment" "github_action_role_write_ssm" {
  role       = aws_iam_role.github_action_role.name
  policy_arn = aws_iam_policy.ssm_writer_policy.arn
}

resource "aws_iam_role_policy_attachment" "github_action_role_push_ecr" {
  role       = aws_iam_role.github_action_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_role_policy_attachment" "github_action_role_eks_access" {
  role       = aws_iam_role.github_action_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_policy" "github_action_eks_deploy_policy" {
  name = "github-action-eks-deploy-policy"
  description = "Policy for GitHub Actions to deploy to EKS"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "eks:DescribeCluster",
          "eks:ListClusters",
          "eks:AccessKubernetesApi"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:eks:${var.aws_region}:${var.aws_account}:cluster/idp"
        ]
      },
      {
        Action = [
          "iam:GetRole",
          "iam:ListRoles",
          "iam:PassRole"
        ]
        Effect = "Allow"
        Resource = [
          "arn:aws:iam::${var.aws_account}:role/watcher-pod-role"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_action_role_eks_deploy" {
  role       = aws_iam_role.github_action_role.name
  policy_arn = aws_iam_policy.github_action_eks_deploy_policy.arn
}


resource "aws_iam_openid_connect_provider" "oidc_github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

