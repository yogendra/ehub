from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

# Import activities
with workflow.unsafe.imports_passed_through():
    from .activities import checkout, build, e2e_test, deploy_to_test, deploy_to_prod


@dataclass
class CICDRequest:
    project: str
    sha: str


@dataclass
class CICDState:
    approved: bool = False
    decided: bool = False


@dataclass
class CICDResult:
    status: str


@workflow.defn
class CICDWorkflow:

    @workflow.init
    def __init__(self, request: CICDRequest):
        self.state = CICDState()

    @workflow.run
    async def run(self, request: CICDRequest) -> CICDResult:

        # 1. Checkout
        result = await workflow.execute_activity(
            checkout, request, start_to_close_timeout=timedelta(minutes=10)
        )
        # 2. Build
        result = await workflow.execute_activity(
            build, request, start_to_close_timeout=timedelta(minutes=10)
        )
        # 3. Deploy to test
        result = await workflow.execute_activity(
            deploy_to_test, request, start_to_close_timeout=timedelta(minutes=10)
        )

        # 3. Wait for approval to deploy to prod
        await workflow.wait_condition(
            lambda: self.state.decided, timeout=timedelta(days=7)
        )

        if not self.state.approved:
            raise Exception("Deployment to prod not approved")

        # 4. Deploy to prod
        result = await workflow.execute_activity(
            deploy_to_prod, request, start_to_close_timeout=timedelta(minutes=10)
        )

        return CICDResult(
            status=result if isinstance(result, str) else result.get("status", ""),
        )

    @workflow.signal
    async def approve(self, approved: bool) -> None:
        self.state.approved = approved
        self.state.decided = True

    @workflow.query
    def get_state(self) -> CICDState:
        return self.state
