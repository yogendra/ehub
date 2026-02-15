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

variable "ec2_instance_id" {
  description = "The ID of the EC2 instance to attach to the LB"
  type        = string
}



variable "security_group_id" {
  description = "Security group ID for the LB"
  type        = string
}

local {
  ports = [80, 443]
}
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  filter {
    name   = "tag:Name"
    values = ["*public*"]
  }
}

resource "aws_lb" "app" {
  name               = "${var.project_id}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [var.security_group_id]
  subnets            = data.aws_subnets.public.ids

  tags = {
    Name = "${var.project_id}-lb"
  }
}

resource "aws_lb_target_group" "app" {
  name     = "${var.project_id}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_target_group_attachment" "app" {
  target_group_arn = aws_lb_target_group.app.arn
  target_id        = var.ec2_instance_id
  port             = 80
}

resource "aws_lb_listener" "app" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

output "lb_arn" {
  description = "The ARN of the Load Balancer"
  value       = aws_lb.app.arn
}

output "lb_dns_name" {
  description = "The DNS name of the Load Balancer"
  value       = aws_lb.app.dns_name
}

output "lb_zone_id" {
  description = "The zone ID of the Load Balancer"
  value       = aws_lb.app.zone_id
}
