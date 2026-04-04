resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}
resource "aws_s3_bucket" "my_llama_bucket" {
  bucket = "my-llama-bucket-${random_string.bucket_suffix.result}"
}
output "my_llama_bucket" {
  description = "Llama Model Assets Bucket."
  value = "${aws_s3_bucket.my_llama_bucket.id}"
}