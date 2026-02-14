from temporalio import activity
import time


@activity.defn
async def checkout(request) -> str:
    activity.logger.info(f"Checkout code from git")

    # Mock terraform execution
    time.sleep(2)

    return "/tmp/code"


@activity.defn
async def build(request) -> str:
    activity.logger.info(f"Build code")

    # Mock terraform execution
    time.sleep(2)

    return "success"


@activity.defn
async def deploy_to_test(request) -> str:
    activity.logger.info(f"Deploy to test")

    # Mock terraform execution
    time.sleep(2)

    return "success"


@activity.defn
async def e2e_test(request) -> str:
    activity.logger.info(f"E2E test")

    # Mock terraform execution
    time.sleep(2)

    return "success"


@activity.defn
async def deploy_to_prod(request) -> str:
    activity.logger.info(f"Deploy to prod")

    # Mock terraform execution
    time.sleep(2)

    return "success"
