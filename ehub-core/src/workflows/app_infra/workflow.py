from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

# Import activities
with workflow.unsafe.imports_passed_through():
    from .activities import provision_ec2, provision_lb, provision_dns


@dataclass
class AppInfraRequest:
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
            "vpc_id": request.vpc_id,
            "subnet_id": request.subnet_id,
            "security_group_id": request.security_group_id,
            "key_name": request.key_name,
            "region": request.region,
            "size": request.size,
        }
        result = await workflow.execute_activity(
            provision_ec2, ec2_request, start_to_close_timeout=timedelta(minutes=10)
        )
        lb_request = {"ec2_id": result.get("ec2_id")}

        result = await workflow.execute_activity(
            provision_lb, lb_request, start_to_close_timeout=timedelta(minutes=10)
        )
        dns_request = {"lb_url": result.get("lb_url")}

        result = await workflow.execute_activity(
            provision_dns, dns_request, start_to_close_timeout=timedelta(minutes=10)
        )
        url = result if isinstance(result, str) else result.get("url", "")

        return AppInfraResult(url=url)
