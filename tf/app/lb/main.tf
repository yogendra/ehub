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

variable "ports" {
  description = "List of ports for the LB to listen on"
  type        = list(number)
}

variable "subnets" {
  description = "List of subnets for the LB (required for ALB)"
  type        = list(string)
}

variable "security_groups" {
  description = "List of security groups for the LB"
  type        = list(string)
}

resource "aws_lb" "app" {
  name               = "${var.project_id}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.security_groups
  subnets            = var.subnets

  tags = {
    Name = "${var.project_id}-lb"
  }
}

resource "aws_lb_target_group" "app" {
  for_each = toset([for p in var.ports : tostring(p)])
  name     = "${var.project_id}-tg-${each.key}"
  port     = tonumber(each.key)
  protocol = "HTTP"
  vpc_id   = var.vpc_id
}

resource "aws_lb_target_group_attachment" "app" {
  for_each         = aws_lb_target_group.app
  target_group_arn = each.value.arn
  target_id        = var.ec2_instance_id
  port             = each.value.port
}

resource "aws_lb_listener" "app" {
  for_each          = aws_lb_target_group.app
  load_balancer_arn = aws_lb.app.arn
  port              = each.value.port
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = each.value.arn
  }
}

output "lb_id" {
  description = "The ID of the Load Balancer"
  value       = aws_lb.app.id
}

output "lb_dns_name" {
  description = "The DNS name of the Load Balancer"
  value       = aws_lb.app.dns_name
}

output "lb_zone_id" {
  description = "The zone ID of the Load Balancer"
  value       = aws_lb.app.zone_id
}
