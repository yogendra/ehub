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

variable "lb_id" {
  description = "The ARN/ID of the load balancer"
  type        = string
}

variable "route53_zone_id" {
  description = "The Route53 hosted zone ID"
  type        = string
}

data "aws_lb" "selected" {
  arn = var.lb_id
}

resource "aws_route53_record" "app" {
  zone_id = var.route53_zone_id
  name    = var.hostname
  type    = "A"

  alias {
    name                   = data.aws_lb.selected.dns_name
    zone_id                = data.aws_lb.selected.zone_id
    evaluate_target_health = true
  }
}

output "fqdn" {
  description = "The fully qualified domain name"
  value       = aws_route53_record.app.fqdn
}
