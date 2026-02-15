# Troubleshooting

## Delete VPC created by test flow

```bash
cd tf/core/vpc
terraform destroy -state ./states/core-infra-test-yogi/terraform.tfstate -var=project_id=test-project -var=region=us-east-1 -var=vpc_cidr=10.0.0.0/16
cd -
```
