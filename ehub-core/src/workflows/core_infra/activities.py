from temporalio import activity
import os
from infra.tf_wrapper.main import TFWrapper
from typing import Any

import logging

logger = logging.getLogger(__name__)


def get_tf_client(activity_name: str, workflow_id: str):
    # TFWrapper handles the base directory (tf_root) internally.
    # We just need to provide the relative path to the core project
    # and the specific state file path (relative to the project's states/ dir).
    working_dir = f"core/{activity_name}"
    state_file_path = f"{workflow_id}"
    return TFWrapper(working_dir=working_dir, state_file_path=state_file_path)


@activity.defn
async def provision_vpc(request: dict[str, Any]) -> dict:
    info = activity.info()
    workflow_id = info.workflow_id

    vpc_cidr = request["vpc_cidr"]
    region = request["region"]
    project_id = request["project_id"]
    destroy = request["destroy"]

    activity.logger.info(
        f"Provisioning actual VPC with CIDR {vpc_cidr} in {region} for workflow {workflow_id}"
    )

    tf = get_tf_client("vpc", workflow_id)
    tf.init()
    tfvars = {"region": region, "vpc_cidr": vpc_cidr, "project_id": project_id}
    result = tf.apply(vars=tfvars, destroy=destroy)

    if result.rc != 0:
        activity.logger.error(f"Terraform failed: {result.stderr}")
        raise Exception(f"Terraform failed: {result.stderr}")

    return {
        "vpc_id": result.get_output_value("vpc_id"),
        "subnet_ids": result.get_output_value("subnet_ids"),
    }


@activity.defn
async def provision_sg(request: dict[str, Any]) -> dict:
    info = activity.info()
    workflow_id = info.workflow_id

    vpc_id = request["vpc_id"]
    region = request["region"]
    project_id = request["project_id"]
    destroy = request["destroy"]

    activity.logger.info(f"Provisioning security groups for VPC {vpc_id} in {region}")

    tf = get_tf_client("sg", workflow_id)
    tf.init()
    tfvars = {"region": region, "vpc_id": vpc_id, "project_id": project_id}
    result = tf.apply(vars=tfvars, destroy=destroy)

    if result.rc != 0:
        activity.logger.error(f"Terraform failed: {result.stderr}")
        raise Exception(f"Terraform failed: {result.stderr}")

    return {"security_group_id": result.get_output_value("security_group_id")}


@activity.defn
async def provision_sshkey(request: dict[str, Any]) -> dict:
    info = activity.info()
    workflow_id = info.workflow_id

    region = request["region"]
    project_id = request["project_id"]
    public_key = request["public_key"]
    destroy = request["destroy"]

    activity.logger.info(f"Adding ssh key in {region}")

    tf = get_tf_client("sshkey", workflow_id)
    tf.init()
    tfvars = {"region": region, "project_id": project_id, "public_key": public_key}
    result = tf.apply(vars=tfvars, destroy=destroy)

    if result.rc != 0:
        activity.logger.error(f"Terraform failed: {result.stderr}")
        raise Exception(f"Terraform failed: {result.stderr}")

    return {"key_name": result.get_output_value("key_name")}
