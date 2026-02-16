from dataclasses import dataclass, field
from datetime import timedelta
from temporalio import workflow
import copy
import logging

logger = logging.getLogger(__name__)

# Import activities
with workflow.unsafe.imports_passed_through():
    from .activities import provision_vpc, provision_sg, provision_sshkey


@dataclass
class CoreInfraRequest:
    project_id: str
    region: str
    public_key: str


@dataclass
class ApprovalBody:
    approved: bool
    cidr: str


@dataclass
class CoreInfraState:
    vpc_id: str = None
    vpc_cidr: str = None
    subnet_ids: list[str] = field(default_factory=list)
    security_group_id: str = None
    key_name: str = None
    public_key: str = None
    approved: bool = False
    decided: bool = False
    status: str = "NEW"
    project_id: str = None
    region: str = "us-east-1"

    def copy_as_dict(self):
        return copy.deepcopy(self.__dict__)


@workflow.defn
class CoreInfraWorkflow:

    @workflow.init
    def __init__(self, request: CoreInfraRequest):
        self.state = CoreInfraState(
            public_key=request.public_key,
            project_id=request.project_id,
            region=request.region,
        )

    @workflow.run
    async def run(self, request: CoreInfraRequest) -> None:
        logger.info(f"CoreInfraWorkflow run: {request}")

        logger.info(f"Waiting for approval")
        # 1. Human In Loop: Approval
        await workflow.wait_condition(
            lambda: self.state.decided, timeout=timedelta(days=7)
        )

        if not self.state.approved:
            logger.info(f"Not approved")
            raise Exception("Not approved")

        logger.info(f"Provisioning infrastructure")
        while not self.state.status == "DELETED":
            logger.info(f"Updating infrastructure")
            await self.update_infra()

            self.state.status = "READY"
            await workflow.wait_condition(lambda: not self.state.status == "READY")

        logger.info(f"Destroying infrastructure")
        await self.destroy_infra()

    async def update_infra(self):
        activity_data = self.state.copy_as_dict()
        activity_data["destroy"] = activity_data["status"] == "DELETED"

        # 1. Provision SSH Key
        result = await workflow.execute_activity(
            provision_sshkey,
            activity_data,
            start_to_close_timeout=timedelta(minutes=10),
        )
        logger.info(f"Done provisioning SSH Key")

        self.state.key_name = result.get("key_name")

        activity_data["key_name"] = self.state.key_name
        logger.info(f"Updating infrastructure with activity data: {activity_data}")

        # 2. Provision VPC
        result = await workflow.execute_activity(
            provision_vpc,
            activity_data,
            start_to_close_timeout=timedelta(minutes=10),
        )
        logger.info(f"Done provisioning VPC")

        self.state.vpc_id = result["vpc_id"]
        self.state.subnet_ids = result["subnet_ids"]

        activity_data["vpc_id"] = self.state.vpc_id
        activity_data["subnet_ids"] = self.state.subnet_ids

        logger.info(f"Updating infrastructure with activity data: {activity_data}")
        # 3. Provision Security Group
        result = await workflow.execute_activity(
            provision_sg,
            activity_data,
            start_to_close_timeout=timedelta(minutes=10),
        )
        logger.info(f"Done provisioning Security Group")

        self.state.security_group_id = result["security_group_id"]
        logger.info(f"Updating infrastructure with activity data: {activity_data}")

    async def destroy_infra(self):
        activity_data = self.state.copy_as_dict()
        activity_data["destroy"] = activity_data["status"] == "DELETED"

        try:
            result = await workflow.execute_activity(
                provision_sg,
                activity_data,
                start_to_close_timeout=timedelta(minutes=10),
            )
            self.state.security_group_id = None
        except Exception as e:
            logger.warn(e)

        try:
            result = await workflow.execute_activity(
                provision_vpc,
                activity_data,
                start_to_close_timeout=timedelta(minutes=10),
            )
            self.state.vpc_id = None
            self.state.subnet_ids = None
        except Exception as e:
            logger.warn(e)

        try:
            result = await workflow.execute_activity(
                provision_sshkey,
                activity_data,
                start_to_close_timeout=timedelta(minutes=10),
            )
            self.state.key_name = None
        except Exception as e:
            logger.warn(e)

    @workflow.signal
    async def approve(self, approval: ApprovalBody) -> None:
        self.state.approved = approval.approved
        self.state.vpc_cidr = approval.cidr
        self.state.decided = True

    @workflow.signal
    def decommission(self) -> None:
        """Signal to decommission the hardware."""
        self.state.status = "DELETED"

    @workflow.signal
    def update(self) -> None:
        """Signal to trigger a hardware upgrade (e.g., resizing nodes)."""
        if self.state.status != "DELETED":
            self.state.status = "MAINTENANCE"

    @workflow.query
    def get_state(self) -> CoreInfraState:
        return self.state
