from temporalio import activity
import time


@activity.defn
async def provision_vpc(request) -> dict:

    vpc_cidr = (
        request.get("vpc_cidr")
        if isinstance(request, dict)
        else getattr(request, "vpc_cidr", "unknown")
    )
    region = (
        request.get("region")
        if isinstance(request, dict)
        else getattr(request, "region", "unknown")
    )

    activity.logger.info(f"Provisioning core infra for VPC {vpc_cidr} in {region}")

    # Mock terraform execution
    time.sleep(2)

    return {
        "vpc_id": "vpc-12345678",
        "subnet_ids": ["subnet-1", "subnet-2"],
        "status": "success",
    }


@activity.defn
async def provision_sg(request) -> dict:
    vpc_cidr = (
        request.get("vpc_cidr")
        if isinstance(request, dict)
        else getattr(request, "vpc_cidr", "unknown")
    )
    region = (
        request.get("region")
        if isinstance(request, dict)
        else getattr(request, "region", "unknown")
    )

    activity.logger.info(f"Provisioning security groups for VPC {vpc_cidr} in {region}")

    # Mock terraform execution
    time.sleep(2)

    return {"security_groups": "sg-12345"}


@activity.defn
async def provision_sshkey(request) -> dict:
    region = (
        request.get("region")
        if isinstance(request, dict)
        else getattr(request, "region", "unknown")
    )
    activity.logger.info(f"Adding ssh key in {region}")

    # Mock terraform execution
    time.sleep(2)

    return {"ssh_key": "key-12345"}
