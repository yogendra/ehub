from temporalio import activity
import time


@activity.defn
async def provision_ec2(request) -> dict:
    activity.logger.info(f"Provisioning ec2 machine")

    # Mock terraform execution
    time.sleep(2)

    return {"ec2_id": "ec2-12345"}


@activity.defn
async def provision_lb(request) -> dict:
    activity.logger.info(f"Adding load balancer")

    # Mock terraform execution
    time.sleep(2)

    return {
        "lb_id": "lb-12345",
        "lb_url": "https://elb-12345.us-east-1.elb.amazonaws.com",
    }


@activity.defn
async def provision_dns(request) -> str:
    activity.logger.info(f"Provisioning app dns")

    # Mock terraform execution
    time.sleep(2)

    return "https://example.com"
