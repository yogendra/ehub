module "test" {
  source          = "../"
  region          = "us-east-1"
  project_id      = "test-project"
  hostname        = "app.example.com"
  lb_id           = "arn:aws:elasticloadbalancing:us-east-1:123456789012:loadbalancer/app/my-load-balancer/50dc6c495c0c9188"
  route53_zone_id = "Z123456789"
}

output "fqdn" {
  value = module.test.fqdn
}
