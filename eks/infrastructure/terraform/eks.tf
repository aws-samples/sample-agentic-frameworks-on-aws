################################################################################
# Cluster
################################################################################

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = var.name
  cluster_version = "1.32"

  iam_role_use_name_prefix = false
  iam_role_name            = "${local.name}-eks-cluster-role"

  node_iam_role_use_name_prefix = false
  node_iam_role_name            = "${local.name}-eks-node-role"

  # Give the Terraform identity admin access to the cluster
  # which will allow it to deploy resources into the cluster
  enable_cluster_creator_admin_permissions = true
  cluster_endpoint_public_access           = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_compute_config = {
    enabled    = true
    node_pools = ["general-purpose"]
  }

  tags = local.tags
}

output "configure_kubectl" {
  description = "Configure kubectl: make sure you're logged in with the correct AWS profile and run the following command to update your kubeconfig"
  value       = "aws eks --region ${local.region} update-kubeconfig --name ${module.eks.cluster_name}"
}

################################################################################
# Adot and Cert Manager Add-ons
################################################################################

module "eks_blueprints_addons" {
  source  = "aws-ia/eks-blueprints-addons/aws"
  version = "~> 1.16"

  cluster_name      = module.eks.cluster_name
  cluster_endpoint  = module.eks.cluster_endpoint
  cluster_version   = module.eks.cluster_version
  oidc_provider_arn = module.eks.oidc_provider_arn

  # EKS Add-on
  eks_addons = {
    adot                            = {}
    amazon-cloudwatch-observability = {}
  }

  # Add-ons
  enable_cert_manager = true


  tags = local.tags

  depends_on = [module.eks]
}

################################################################################
# Container Insights Pod Identity
################################################################################

module "container_insights_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 1.0"

  ## IAM role / policy
  name            = "${local.name}-cloudwatch-agent"
  use_name_prefix = false

  ## Pod-identity association
  associations = {
    portfolio-manager = {
      cluster_name    = module.eks.cluster_name
      namespace       = "amazon-cloudwatch"
      service_account = "cloudwatch-agent"
    },
  }

  additional_policy_arns = {
    CloudWatchAgentServerPolicy = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
    AWSXrayWriteOnlyAccess      = "arn:aws:iam::aws:policy/AWSXrayWriteOnlyAccess"
  }

  tags = local.tags
}

################################################################################
# Bedrock Model Invocation Logging
################################################################################

module "bedrock_logging_role" {
  source = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"

  create_role                     = true
  create_custom_role_trust_policy = true
  custom_role_trust_policy        = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "${data.aws_caller_identity.current.account_id}"
        },
        "ArnLike": {
          "aws:SourceArn": "arn:aws:bedrock:${local.region}:${data.aws_caller_identity.current.account_id}:*"
        }
      }
    }
  ]
}
EOF

  role_name         = "${local.name}-bedrock-logging-role"
  role_requires_mfa = false

  custom_role_policy_arns = [
    module.iam_policy.arn,
  ]
  number_of_custom_role_policy_arns = 1
}


module "iam_policy" {
  source = "terraform-aws-modules/iam/aws//modules/iam-policy"

  name        = "${local.name}-bedrock-logging-policy"
  path        = "/"
  description = "Policy for Bedrock model invocation logging"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

module "log_group" {
  source  = "terraform-aws-modules/cloudwatch/aws//modules/log-group"
  version = "~> 3.0"

  name              = "/aws/bedrock/model-invocation"
  retention_in_days = 120
}

resource "aws_bedrock_model_invocation_logging_configuration" "this" {

  logging_config {
    embedding_data_delivery_enabled = true
    image_data_delivery_enabled     = true
    text_data_delivery_enabled      = true
    video_data_delivery_enabled     = true

    cloudwatch_config {
      log_group_name = "/aws/bedrock/model-invocation"
      role_arn       = module.bedrock_logging_role.iam_role_arn
    }
  }
}
