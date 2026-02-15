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

variable "project_id"{
    type = string
}


variable "public_key"{
    type = string
}

resource "aws_key_pair" "deployer" {
  key_name_prefix   = "deployer-key"
  public_key = var.public_key
}

output "key_name" {
  value = aws_key_pair.deployer.key_name
}
