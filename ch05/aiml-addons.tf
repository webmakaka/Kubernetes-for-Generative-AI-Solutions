resource "kubernetes_namespace" "jupyterhub" {
  metadata {
    name = "jupyterhub"
  }
}

provider "random" {}

resource "random_password" "jupyter_pwd" {
  length  = 16
  special = true
  override_special = "_%@"
}

output "jupyter_pwd" {
  value = random_password.jupyter_pwd.result
  sensitive = true
}

module "jupyterhub_single_user_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name = "${module.eks.cluster_name}-jupyterhub-single-user-sa"

  role_policy_arns = {
    policy = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" 
  }

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["${kubernetes_namespace.jupyterhub.metadata[0].name}:${module.eks.cluster_name}-jupyterhub-single-user"]
    }
  }
}

resource "kubernetes_service_account_v1" "jupyterhub_single_user_sa" {
  metadata {
    name        = "${module.eks.cluster_name}-jupyterhub-single-user"
    namespace   = kubernetes_namespace.jupyterhub.metadata[0].name
    annotations = { "eks.amazonaws.com/role-arn" : module.jupyterhub_single_user_irsa.iam_role_arn }
  }
  automount_service_account_token = true
}

resource "kubernetes_secret_v1" "jupyterhub_single_user" {
  metadata {
    name      = "${module.eks.cluster_name}-jupyterhub-single-user-secret"
    namespace = kubernetes_namespace.jupyterhub.metadata[0].name
    annotations = {
      "kubernetes.io/service-account.name"      = kubernetes_service_account_v1.jupyterhub_single_user_sa.metadata[0].name
      "kubernetes.io/service-account.namespace" = kubernetes_namespace.jupyterhub.metadata[0].name
    }
  }

  type = "kubernetes.io/service-account-token"
}

data "http" "jupyterhub_values" {
  url = "https://kubernetes-for-genai-models.s3.amazonaws.com/chapter5/jupyterhub-values.yaml"
}

locals {
  jupyterhub_values_template = data.http.jupyterhub_values.response_body
  jupyterhub_values_rendered = replace(
       replace(
         replace(
           local.jupyterhub_values_template,
           "$${jupyter_single_user_sa_name}", kubernetes_service_account_v1.jupyterhub_single_user_sa.metadata[0].name
         ),
         "$${region}", local.region
       ),
       "$${jupyter_pwd}", random_password.jupyter_pwd.result
     )
}

module "eks_data_addons" {
  source  = "aws-ia/eks-data-addons/aws"
  version = "~> 1.37" # ensure to update this to the latest/desired version

  oidc_provider_arn = module.eks.oidc_provider_arn

  #---------------------------------------------------------------
  # NVIDIA Device Plugin Add-on
  #---------------------------------------------------------------
  enable_nvidia_device_plugin = true
  nvidia_device_plugin_helm_config = {
    name = "nvidia-device-plugin"
    version = "0.17.1"
  }
  #---------------------------------------------------------------
  # JupyterHub Add-on
  #---------------------------------------------------------------
  enable_jupyterhub = true
  jupyterhub_helm_config = {
    values = [local.jupyterhub_values_rendered]
    version = "3.2.1"
  }
}

module "catalog_rag_api_irsa" {
  source = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"

  role_name = "${module.eks.cluster_name}-catalog-sa"

  role_policy_arns = {
    policy = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess" 
  }

  oidc_providers = {
    main = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["default:catalog-sa"]
    }
  }
}

resource "kubernetes_service_account_v1" "catalog_rag_api_sa" {
  metadata {
    name        = "catalog-sa"
    namespace   = "default"
    annotations = { "eks.amazonaws.com/role-arn" : module.catalog_rag_api_irsa.iam_role_arn }
  }

  automount_service_account_token = true
}


