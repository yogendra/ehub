from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

# Import activities
with workflow.unsafe.imports_passed_through():
    from .activities import provision_ec2, provision_lb, provision_dns


@dataclass
class AppInfraRequest:
    size: str


@dataclass
class AppInfraState:
    url: str = ""


@dataclass
class AppInfraResult:
    url: str


@workflow.defn
class AppInfraWorkflow:

    @workflow.init
    def __init__(self, request: AppInfraRequest):
        self.state = AppInfraState()

    @workflow.run
    async def run(self, request: AppInfraRequest) -> AppInfraResult:

        result = await workflow.execute_activity(
            provision_ec2, request, start_to_close_timeout=timedelta(minutes=10)
        )
        ec2_id = result.get("ec2_id")

        result = await workflow.execute_activity(
            provision_lb, ec2_id, start_to_close_timeout=timedelta(minutes=10)
        )
        lb_url = result.get("lb_url")

        result = await workflow.execute_activity(
            provision_dns, lb_url, start_to_close_timeout=timedelta(minutes=10)
        )
        url = result if isinstance(result, str) else result.get("url", "")
        self.state.url = url

        return AppInfraResult(url=url)

    @workflow.query
    def get_state(self) -> AppInfraState:
        return self.state
