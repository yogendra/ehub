import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
import os
import logging
from workflows.core_infra.workflow import CoreInfraWorkflow
from workflows.core_infra.activities import (
    provision_vpc,
    provision_sg,
    provision_sshkey,
)

from workflows.app_infra.workflow import AppInfraWorkflow
from workflows.app_infra.activities import (
    provision_ec2,
    provision_lb,
    provision_dns,
)
from workflows.cicd.workflow import CICDWorkflow
from workflows.cicd.activities import (
    checkout,
    build,
    e2e_test,
    deploy_to_test,
    deploy_to_prod,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def main():
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    logger.info(f"Connecting to Temporal at {temporal_host}")
    client = await Client.connect(temporal_host)
    logger.info(f"Connected to Temporal at {temporal_host}")

    core_worker = Worker(
        client,
        task_queue="ehub-core-infra",
        workflows=[CoreInfraWorkflow],
        activities=[
            provision_vpc,
            provision_sg,
            provision_sshkey,
        ],
    )

    app_worker = Worker(
        client,
        task_queue="ehub-app-infra",
        workflows=[AppInfraWorkflow],
        activities=[
            provision_ec2,
            provision_lb,
            provision_dns,
        ],
    )

    cicd_worker = Worker(
        client,
        task_queue="ehub-cicd",
        workflows=[CICDWorkflow],
        activities=[
            checkout,
            build,
            e2e_test,
            deploy_to_test,
            deploy_to_prod,
        ],
    )

    logger.info(f"Workers started on {temporal_host}")
    logger.info("Queues: ehub-core-infra, ehub-app-infra, ehub-cicd")

    try:
        await asyncio.gather(
            core_worker.run(),
            app_worker.run(),
            cicd_worker.run(),
        )
    except asyncio.CancelledError:
        logger.info("Main task cancelled, performing cleanup.")
        # Perform cleanup actions here
    finally:
        logger.info("Cleanup finished, exiting.")


if __name__ == "__main__":
    logger.info("Starting worker...")
    asyncio.run(main())
