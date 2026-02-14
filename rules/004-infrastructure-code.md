### 004 Infrastructure as Code Rules

#### Terraform Standards

- **Module Organization**: Organize Terraform code into reusable modules
- **State Management**: Use remote state backend (S3 + DynamoDB for locking)
- **Variable Validation**: Add validation rules to input variables
- **Output Values**: Export all important resource attributes as outputs
- **Tagging**: Apply consistent tags to all resources (Project, Environment, ManagedBy)

#### Opinionated Choices

- **Minimize Options**: Be opinionated to simplify developer experience
- **Sensible Defaults**: Provide production-ready defaults
- **Escape Hatches**: Allow overrides for advanced use cases, but discourage them
- **Documentation**: Document why specific choices were made

#### Resource Naming

- **Consistent Convention**: Use consistent naming pattern (e.g., `{project}-{env}-{resource}`)
- **Readable Names**: Make names human-readable and searchable
- **Avoid Abbreviations**: Use full words unless commonly understood (vpc, alb, ec2 are OK)

#### Security

- **Least Privilege**: Grant minimum necessary permissions
- **Secrets Management**: Use AWS Secrets Manager or Parameter Store for secrets
- **Network Isolation**: Use private subnets for application resources
- **Security Groups**: Implement restrictive security group rules
- **Encryption**: Enable encryption at rest and in transit by default

#### Workflow Integration

- **Terraform Wrapper**: Call Terraform through Activities, not directly in workflows
- **State Tracking**: Store Terraform state references in workflow state
- **Rollback Support**: Design for rollback scenarios
- **Drift Detection**: Implement periodic drift detection
