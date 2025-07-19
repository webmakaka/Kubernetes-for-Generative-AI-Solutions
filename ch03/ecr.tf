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
