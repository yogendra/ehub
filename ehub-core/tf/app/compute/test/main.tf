module "test" {
  source     = "../"
  region            = "us-east-1"
  project_id        = "test-project"
  vpc_id            = "vpc-015038551e268c210"
  subnet_id         = "subnet-07b55307470c0d250"
  key_name          = "deployer-key20260215160414942800000001"
  security_group_id = "sg-02986b19beb4f3b84"
  size              = "t3.small"
}

output "ec2_id" {
  value = module.test.ec2_id
}
