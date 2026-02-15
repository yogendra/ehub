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
  description = "AWS region"
  type        = string
}

variable "project_id" {
  description = "Project identifier"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet" {
  description = "Subnet ID"
  type        = string
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

variable "size" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.size
  subnet_id     = var.subnet
  key_name      = var.key_name

  tags = {
    Name = "${var.project_id}-ec2"
  }
}

output "ec2_id" {
  description = "The ID of the EC2 instance"
  value       = aws_instance.app.id
}
