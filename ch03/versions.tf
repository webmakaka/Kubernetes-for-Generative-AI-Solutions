terraform {
  required_version = ">= 1.11"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = ">= 5.96"
    }
    helm = {
      source = "hashicorp/helm"
      version = ">= 2.17"
    }
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">= 2.36"
    }
  }
}
