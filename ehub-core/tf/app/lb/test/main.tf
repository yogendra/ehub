module "test" {
  source          = "../"
  region          = "us-east-1"
  project_id      = "test-project"
  vpc_id          = "vpc-015038551e268c210"
  ec2_instance_id = "i-0265b802a73f631ec"
  security_group_id  = "sg-02986b19beb4f3b84"
}

output "lb_arn" {
  value = module.test.lb_arn
}
