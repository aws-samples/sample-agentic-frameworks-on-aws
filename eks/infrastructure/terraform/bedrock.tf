
################################################################################
# Bedrock Model Invocation Logging
################################################################################

module "bedrock_logging_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.1"

  name = local.name

  trust_policy_permissions = {
    BedrockAssumeRole = {
      principals = [{
        type        = "Service"
        identifiers = ["bedrock.amazonaws.com"]
      }]
      actions = ["sts:AssumeRole"]
      condition = [
        {
          test     = "StringEquals"
          variable = "aws:SourceAccount"
          values   = [data.aws_caller_identity.current.account_id]
        },
        {
          test     = "ArnLike"
          variable = "aws:SourceArn"
          values   = ["arn:aws:bedrock:${data.aws_region.current.id}:${data.aws_caller_identity.current.account_id}:*"]
        }
      ]
    }
  }

  policies = {
    BedrockLoggingPolicy = module.iam_policy.arn
  }

  tags = local.tags
}

module "iam_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 6.1"

  # name_prefix = local.name
  path        = "/"
  description = "Policy for Bedrock model invocation logging"

  policy = <<-EOF
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

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/bedrock/model-invocation"
  retention_in_days = 120

  tags = local.tags
}

resource "aws_bedrock_model_invocation_logging_configuration" "this" {

  logging_config {
    embedding_data_delivery_enabled = true
    image_data_delivery_enabled     = true
    text_data_delivery_enabled      = true
    video_data_delivery_enabled     = true

    cloudwatch_config {
      log_group_name = "/aws/bedrock/model-invocation"
      role_arn       = module.bedrock_logging_role.arn
    }
  }
}
