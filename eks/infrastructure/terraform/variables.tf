variable "name" {
  description = "EKS Cluster name"
  type        = string
  default     = "agentic-ai-on-eks-frameworks-ref-architecture"
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

variable "weather_namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "agents"
}

variable "weather_service_account" {
  description = "Kubernetes service account name"
  type        = string
  default     = "weather-agent"
}

variable "travel_namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "agents"
}

variable "travel_service_account" {
  description = "Kubernetes service account name"
  type        = string
  default     = "travel-agent"
}


variable "bedrock_model_id" {
  description = "Model ID for the agents"
  type        = string
  default     = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
}

# Cognito module variables

variable "cognito_additional_redirect_uri" {
  description = "Additional allowed redirect URI after authorization"
  type        = string
  default     = ""
}

variable "cognito_additional_logout_uri" {
  description = "Additional allowed logout URIs"
  type        = string
  default     = ""
}

variable "cognito_prefix_user_pool" {
  description = "Prefix for user pool"
  type        = string
  default     = "agents-on-eks"
}
