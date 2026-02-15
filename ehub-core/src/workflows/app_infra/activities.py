from temporalio import activity
from infra.tf_wrapper.main import TFWrapper


@activity.defn
async def provision_ec2(request: dict) -> dict:
    project_id = request.get("project_id")
    activity.logger.info(f"Provisioning ec2 machine for project: {project_id}")

    tf = TFWrapper(working_dir="app/compute", state_file_path=project_id)
    try:
        res = tf.init()
        if res.rc != 0:
            raise Exception(f"Terraform init failed: {res.stderr}")

        res = tf.apply(vars=request)
        if res.rc != 0:
            raise Exception(f"Terraform apply failed: {res.stderr}")

        ec2_id = res.get_output_value("ec2_id")
        activity.logger.info(f"EC2 provisioned: {ec2_id}")

        return {"ec2_id": ec2_id}
    finally:
        tf.cleanup()


@activity.defn
async def provision_lb(request: dict) -> dict:
    project_id = request.get("project_id")
    activity.logger.info(f"Adding load balancer for project: {project_id}")

    tf = TFWrapper(working_dir="app/lb", state_file_path=project_id)
    try:
        res = tf.init()
        if res.rc != 0:
            raise Exception(f"Terraform init failed: {res.stderr}")

        res = tf.apply(vars=request)
        if res.rc != 0:
            raise Exception(f"Terraform apply failed: {res.stderr}")

        lb_arn = res.get_output_value("lb_arn")
        activity.logger.info(f"Load balancer provisioned: {lb_arn}")

        return {
            "lb_arn": lb_arn,
        }
    finally:
        tf.cleanup()


@activity.defn
async def provision_dns(request: dict) -> dict:
    project_id = request.get("project_id")
    activity.logger.info(f"Provisioning app dns for project: {project_id}")

    tf = TFWrapper(working_dir="app/dns", state_file_path=project_id)
    try:
        res = tf.init()
        if res.rc != 0:
            raise Exception(f"Terraform init failed: {res.stderr}")

        res = tf.apply(vars=request)
        if res.rc != 0:
            raise Exception(f"Terraform apply failed: {res.stderr}")

        url = res.get_output_value("url")
        activity.logger.info(f"DNS provisioned: {url}")

        return {"url": url}
    finally:
        tf.cleanup()
