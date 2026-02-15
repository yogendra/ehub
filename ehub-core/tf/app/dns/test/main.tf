module "test" {
  source           = "../"
  region           = "us-east-1"
  project_id       = "test-project"
  hostname         = "app"
  lb_arn           = "arn:aws:elasticloadbalancing:us-east-1:503014014885:loadbalancer/app/test-project-lb/389a80fbe7d2ec64"
  hosted_zone_name = "demo.yogendra.me"
}

output "url" {
  value = module.test.url
}
