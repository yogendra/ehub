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

variable "hostname" {
  description = "The hostname for the DNS record"
  type        = string
}

variable "lb_arn" {
  description = "The ARN of the load balancer"
  type        = string
}

variable "hosted_zone_name" {
  description = "The route53hosted zone name"
  type        = string
}

data "aws_lb" "selected" {
  arn = var.lb_arn
}

data "aws_route53_zone" "selected" {
  name = var.hosted_zone_name
}

resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = var.hostname
  type    = "A"

  alias {
    name                   = data.aws_lb.selected.dns_name
    zone_id                = data.aws_lb.selected.zone_id
    evaluate_target_health = true
  }
}

output "url" {
  description = "FQDN / URL of the application"
  value       = aws_route53_record.app.fqdn
}
