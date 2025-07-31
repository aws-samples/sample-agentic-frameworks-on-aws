module "weather_agent_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 1.0"

  ## IAM role / policy
  name                 = "${local.name}-bedrock-role"
  attach_custom_policy = true
  policy_statements = [
    {
      sid = "BedrockAccess"
      actions = [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ]
      resources = ["*"]
    },
    {
      sid = "AccessBucket"
      actions = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ]
      resources = ["${aws_s3_bucket.weather_agent_session_store.arn}/*"]
    },
    {
      sid = "AccessBuckets"
      actions = [
        "s3:ListBucket",
      ]
      resources = [aws_s3_bucket.weather_agent_session_store.arn]
    }
  ]

  ## Pod-identity association
  associations = {
    weather-agent = {
      cluster_name    = module.eks.cluster_name
      namespace       = var.weather_namespace
      service_account = var.weather_service_account
    }
  }

  tags = local.tags
}

module "travel_agent_pod_identity" {
  source  = "terraform-aws-modules/eks-pod-identity/aws"
  version = "~> 1.0"

  ## IAM role / policy
  name                 = "${local.name}-travel-agent-bedrock-role"
  attach_custom_policy = true
  policy_statements = [
    {
      sid = "BedrockAccess"
      actions = [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ]
      resources = ["*"]
    },
    {
      sid = "AccessBucket"
      actions = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ]
      resources = ["${aws_s3_bucket.travel_agent_session_store.arn}/*"]
    },
    {
      sid = "AccessBuckets"
      actions = [
        "s3:ListBucket",
      ]
      resources = [aws_s3_bucket.travel_agent_session_store.arn]
    }
  ]

  ## Pod-identity association
  associations = {
    travel-agent = {
      cluster_name    = module.eks.cluster_name
      namespace       = var.travel_namespace
      service_account = var.travel_service_account
    }
  }

  tags = local.tags
}

