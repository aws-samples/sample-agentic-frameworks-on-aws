terraform {
  required_version = "1.13.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "6.19.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.9.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}
