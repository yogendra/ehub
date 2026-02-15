terraform {
  backend "local" {}
}
provider "aws" {
  region = var.region
  default_tags {
    tags = {
      project_id = var.project_id
    }
  }
}

variable "region" {
  type = string
}

variable "project_id" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

data "aws_availability_zones" "available" {}

locals {
  num_azs         = min(3, length(data.aws_availability_zones.available.names))
  private_subnets = [for i in range(local.num_azs) : cidrsubnet(var.vpc_cidr, 8, i)]
  public_subnets  = [for i in range(local.num_azs) : cidrsubnet(var.vpc_cidr, 8, i + local.num_azs)]
}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.project_id}-vpc"
  cidr = var.vpc_cidr

  azs             = data.aws_availability_zones.available.names
  private_subnets = local.private_subnets
  public_subnets  = local.public_subnets

  enable_nat_gateway = false
  single_nat_gateway = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
    Project     = var.project_id
  }
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "subnet_ids" {
  value = module.vpc.private_subnets
}