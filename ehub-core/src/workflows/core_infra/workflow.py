from dataclasses import dataclass, field
from datetime import timedelta
from temporalio import workflow


# Import activities
with workflow.unsafe.imports_passed_through():
    from .activities import provision_vpc, provision_sg, provision_sshkey


@dataclass
class CoreInfraRequest:
    project_id: str
    region: str


@dataclass
class ApprovalBody:
    approved: bool
    cidr: str


@dataclass
class CoreInfraState:
    vpc_id: str = ""
    vpc_cidr: str = ""
    subnet_ids: list[str] = field(default_factory=list)
    security_groups: list[str] = field(default_factory=list)
    ssh_key: str = ""
    approved: bool = False
    decided: bool = False


@dataclass
class CoreInfraResult:
    vpc_id: str
    subnet_ids: list[str]
    success: bool


@workflow.defn
class CoreInfraWorkflow:

    @workflow.init
    def __init__(self, request: CoreInfraRequest):
        self.state = CoreInfraState()

    @workflow.run
    async def run(self, request: CoreInfraRequest) -> CoreInfraResult:

        # 1. Human In Loop: Approval
        await workflow.wait_condition(
            lambda: self.state.decided, timeout=timedelta(days=7)
        )

        if not self.state.approved:
            raise Exception("Not approved")

        # 2. Execute Activity
        activity_data = {
            "project_id": request.project_id,
            "region": request.region,
            "vpc_cidr": self.state.vpc_cidr,
        }

        result = await workflow.execute_activity(
            provision_vpc,
            activity_data,
            start_to_close_timeout=timedelta(minutes=10),
        )

        self.state.vpc_id = result.get("vpc_id", "")
        self.state.subnet_ids = result.get("subnet_ids", [])

        # 3. Provision Security Group
        result = await workflow.execute_activity(
            provision_sg,
            activity_data,
            start_to_close_timeout=timedelta(minutes=10),
        )

        self.state.security_groups = result.get("security_groups", [])

        # 4. Provision SSH Key
        result = await workflow.execute_activity(
            provision_sshkey,
            activity_data,
            start_to_close_timeout=timedelta(minutes=10),
        )

        return CoreInfraResult(
            vpc_id=self.state.vpc_id,
            subnet_ids=self.state.subnet_ids,
            success=True,
        )

    @workflow.signal
    async def approve(self, approval: ApprovalBody) -> None:
        self.state.approved = approval.approved
        self.state.vpc_cidr = approval.cidr
        self.state.decided = True

    @workflow.query
    def get_state(self) -> CoreInfraState:
        return self.state
