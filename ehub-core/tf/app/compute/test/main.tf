module "test" {
  source     = "../"
  region     = "us-east-1"
  project_id = "test-project"
  vpc_id     = "vpc-12345678"
  subnet     = "subnet-12345678"
  key_name   = "test-key"
  size       = "t3.small"
}

output "ec2_id" {
  value = module.test.ec2_id
}
