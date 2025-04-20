data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "availability-zone"
    values = ["us-east-1a", "us-east-1b", "us-east-1c"]
  }
  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

resource "aws_eks_cluster" "idp" {
  name = "idp"
  role_arn = aws_iam_role.idp_node_role.arn
  vpc_config {
    subnet_ids = data.aws_subnets.default.ids
    security_group_ids = [aws_security_group.cluster_sg.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}

resource "aws_security_group" "cluster_sg" {
  name = "cluster_sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_iam_role" "idp_node_role" {
  name = "idp_node_role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": ["ec2.amazonaws.com", "eks.amazonaws.com"]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "idp_node_role_attach_ecr" {
  role       = aws_iam_role.idp_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_role_policy_attachment" "idp_node_role_attach_cni" {
  role       = aws_iam_role.idp_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "idp_node_role_attach_cluster" {
  role       = aws_iam_role.idp_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "idp_node_role_attach_node" {
  role       = aws_iam_role.idp_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_eks_addon" "eks_addon_cni" {
  cluster_name      = aws_eks_cluster.idp.name
  addon_name        = "vpc-cni"
  addon_version     = "v1.19.3-eksbuild.1"
}

resource "aws_eks_addon" "eks_addon_kube_proxy" {
  cluster_name      = aws_eks_cluster.idp.name
  addon_name        = "kube-proxy"
  addon_version     = "v1.32.0-eksbuild.2"
  depends_on        = [aws_eks_addon.eks_addon_cni]
}

resource "aws_eks_addon" "eks_addon_coredns" {
  cluster_name      = aws_eks_cluster.idp.name
  addon_name        = "coredns"
  addon_version     = "v1.11.4-eksbuild.2"
  depends_on        = [aws_eks_addon.eks_addon_kube_proxy]
}

resource "aws_eks_addon" "eks-addon-eks-pod-identity-agent" {
  cluster_name      = aws_eks_cluster.idp.name
  addon_name        = "eks-pod-identity-agent"
  addon_version     = "v1.0.0-eksbuild.1"
  depends_on        = [aws_eks_addon.eks_addon_coredns]
}

resource "aws_eks_node_group" "arm_node_group" {
  cluster_name    = aws_eks_cluster.idp.name
  node_group_name = "arm_node_group"
  node_role_arn   = aws_iam_role.idp_node_role.arn
  subnet_ids      = data.aws_subnets.default.ids
  scaling_config {
    desired_size = 8
    max_size     = 8
    min_size     = 0
  }
  instance_types  = ["t3.micro"]
  ami_type        = "AL2_x86_64"
}

# Output the OIDC provider ARN
output "oidc_provider_arn" {
  value = replace(aws_eks_cluster.idp.identity[0].oidc[0].issuer, "https://", "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/")
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

locals {
  oidc_provider_url = aws_eks_cluster.idp.identity[0].oidc[0].issuer
  eks_oidc_provider_url = replace(aws_eks_cluster.idp.identity[0].oidc[0].issuer, "https://", "")
}



