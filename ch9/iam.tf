data "aws_iam_policy_document" "my_llama_app_trust_policy" {
  statement {
    actions = ["sts:AssumeRole", "sts:TagSession"]
    effect  = "Allow"
    principals {
      type        = "Service"
      identifiers = ["pods.eks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "my_llama_app_role" {
  name               = "my-llama-app-role"
  assume_role_policy = data.aws_iam_policy_document.my_llama_app_trust_policy.json
}

resource "aws_iam_policy" "hf_secrets_access_policy" {
  name        = "hf-secrets-access-policy"
  description = "Policy to access hugging-face-secret in Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:${local.region}:${data.aws_caller_identity.current.account_id}:secret:hugging-face-secret*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "hf_secrets_policy_attachment" {
  role       = aws_iam_role.my_llama_app_role.name
  policy_arn = aws_iam_policy.hf_secrets_access_policy.arn
}

resource "aws_eks_pod_identity_association" "my_llama_sa_pod_identity" {
  cluster_name    = module.eks.cluster_name
  namespace       = "default"
  service_account = "my-llama-sa"
  role_arn        = aws_iam_role.my_llama_app_role.arn
}

data "aws_caller_identity" "current" {}
