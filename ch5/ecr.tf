resource "aws_ecr_repository" "my-llama" {
  name = "my-llama"
  image_tag_mutability = "MUTABLE"
}

output "ecr_push_cmds" {
  description = "Command to authenticate with ECR and push the container image."
  value = <<EOT
  aws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin ${aws_ecr_repository.my-llama.repository_url}
  docker tag my-llama ${aws_ecr_repository.my-llama.repository_url}
  docker push ${aws_ecr_repository.my-llama.repository_url}
  EOT
}

resource "aws_ecr_repository" "my-llama-finetuned" {
  name = "my-llama-finetuned"
  image_tag_mutability = "MUTABLE"
}

output "my_llama_finetuned_ecr_push_cmds" {
  description = "Command to authenticate with ECR and push the my-llama-finetuned container image."
  value = <<EOT
  aws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin ${aws_ecr_repository.my-llama-finetuned.repository_url}
  docker tag my-llama-finetuned ${aws_ecr_repository.my-llama-finetuned.repository_url}
  docker push ${aws_ecr_repository.my-llama-finetuned.repository_url}
  EOT
}

resource "aws_ecr_repository" "rag-app" {
  name = "rag-app"
}

output "rag_app_ecr_push_cmds" {
  description = "Command to authenticate with ECR and push the rag-app container image."
  value = <<EOT
  aws ecr get-login-password --region ${local.region} | docker login --username AWS --password-stdin ${aws_ecr_repository.rag-app.repository_url}
  docker tag rag-app ${aws_ecr_repository.rag-app.repository_url}
  docker push ${aws_ecr_repository.rag-app.repository_url}
  EOT
}
