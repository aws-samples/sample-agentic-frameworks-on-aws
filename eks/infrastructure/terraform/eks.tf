################################################################################
# Cluster
################################################################################

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = var.name
  kubernetes_version = "1.34"

  iam_role_use_name_prefix = false
  iam_role_name            = "${local.name}-eks-cluster-role"

  node_iam_role_use_name_prefix = false
  node_iam_role_name            = "${local.name}-eks-node-role"

  # Give the Terraform identity admin access to the cluster
  # which will allow it to deploy resources into the cluster
  enable_cluster_creator_admin_permissions = true
  endpoint_public_access                   = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  compute_config = {
    enabled    = true
    node_pools = ["general-purpose"]
  }
  addons = {
    amazon-cloudwatch-observability = {
      most_recent                 = true
      resolve_conflicts_on_update = "OVERWRITE"
      pod_identity_association = [{
        role_arn = aws_iam_role.cloudwatch_agent_role.arn
        service_account = "cloudwatch-agent"
        }]
    }
  }

  tags = local.tags

}

################################################################################
# Container Insights Pod Identity
################################################################################

resource "aws_iam_role" "cloudwatch_agent_role" {
  name = "${local.name}-cloudwatch-for-pod-identity"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sts:AssumeRole",
          "sts:TagSession"
        ]
        Principal = {
          Service = "pods.eks.amazonaws.com"
        }
      }
    ]
  })
}
resource "aws_iam_role_policy_attachment" "cloudwatch_agent_policy" {
  role       = aws_iam_role.cloudwatch_agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "xray_write_policy" {
  role       = aws_iam_role.cloudwatch_agent_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
}

