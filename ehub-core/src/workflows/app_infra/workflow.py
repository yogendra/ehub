import os
from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

# Import activities
with workflow.unsafe.imports_passed_through():
    from .activities import provision_ec2, provision_lb, provision_dns

aws_hosted_zone_name = os.getenv("AWS_HOSTED_ZONE_NAME", "demo.yogendra.me")


@dataclass
class AppInfraRequest:
    project_id: str
    vpc_id: str
    subnet_id: str
    security_group_id: str
    key_name: str
    size: str = "t3.micro"
    region: str = "us-east-1"


@dataclass
class AppInfraResult:
    url: str


@workflow.defn
class AppInfraWorkflow:

    @workflow.run
    async def run(self, request: AppInfraRequest) -> AppInfraResult:

        ec2_request = {
            "project_id": request.project_id,
            "region": request.region,
            "vpc_id": request.vpc_id,
            "security_group_id": request.security_group_id,
            "subnet_id": request.subnet_id,
            "key_name": request.key_name,
            "size": request.size,
        }
        result = await workflow.execute_activity(
            provision_ec2, ec2_request, start_to_close_timeout=timedelta(minutes=10)
        )
        lb_request = {
            "project_id": request.project_id,
            "region": request.region,
            "vpc_id": request.vpc_id,
            "security_group_id": request.security_group_id,
            "ec2_instance_id": result.get("ec2_id"),
        }

        result = await workflow.execute_activity(
            provision_lb, lb_request, start_to_close_timeout=timedelta(minutes=10)
        )
        dns_request = {
            "project_id": request.project_id,
            "region": request.region,
            "hostname": request.project_id,
            "lb_arn": result.get("lb_arn"),
            "hosted_zone_name": aws_hosted_zone_name,
        }

        result = await workflow.execute_activity(
            provision_dns, dns_request, start_to_close_timeout=timedelta(minutes=10)
        )

        return AppInfraResult(url=result.get("url"))
