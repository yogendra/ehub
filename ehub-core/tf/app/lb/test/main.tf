module "test" {
  source          = "../"
  region          = "us-east-1"
  project_id      = "test-project"
  vpc_id          = "vpc-12345678"
  ec2_instance_id = "i-12345678"
  ports           = [80, 443]
  subnets         = ["subnet-1", "subnet-2"]
  security_groups = ["sg-1"]
}

output "lb_id" {
  value = module.test.lb_id
}
