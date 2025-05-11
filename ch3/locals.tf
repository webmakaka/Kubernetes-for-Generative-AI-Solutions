data "aws_availability_zones" "azs" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

locals {
  name     = "eks-demo"
  region   = "us-west-2"
  vpc_cidr = "10.0.0.0/16"
  azs      = slice (data.aws_availability_zones.azs.names, 0, 3)
}

