from dataclasses import dataclass
from typing import Any
import subprocess
import os
import json
import logging

logger = logging.getLogger(__name__)

project_root = os.path.abspath(os.getenv("PROJECT_ROOT", "/app"))
state_dir_root = os.path.join(project_root, "tf_states")
tf_root = os.path.join(project_root, "tf")
logger.info(
    f"""
TF Wrapper Project root: {project_root}
TF Wrapper State dir root: {state_dir_root}
TF Wrapper TF root: {tf_root}
"""
)


@dataclass
class TFResult:
    rc: int
    stdout: str
    stderr: str
    output: dict[str, Any]

    def get_output_value(self, key: str, default: Any = None) -> Any:
        if isinstance(self.output, dict) and key in self.output:
            return self.output[key].get("value", default)
        return default


class TFWrapper:
    def __init__(self, working_dir: str, state_file_path: str):

        self.working_dir = os.path.abspath(os.path.join(tf_root, working_dir))
        state_dir = os.path.join(state_dir_root, f"{working_dir}/{state_file_path}")
        self.state_file_path = os.path.join(state_dir, "terraform.tfstate")

        # Ensure working directory exists
        if not os.path.exists(self.working_dir):
            raise ValueError(f"Working directory does not exist: {self.working_dir}")

        # Ensure state directory exists
        os.makedirs(state_dir, exist_ok=True)

    def _run_raw_command(self, cmd: str) -> tuple[int, str, str]:
        logger.debug(f"Running command: {cmd}")
        process = subprocess.Popen(
            cmd,
            shell=True,
            cwd=self.working_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def _run_tf_command(self, cmd: str) -> TFResult:
        rc, stdout, stderr = self._run_raw_command(cmd)
        return TFResult(rc=rc, stdout=stdout, stderr=stderr, output=self.output())

    def init(self) -> TFResult:
        cmd = f"""
        terraform init \
            -reconfigure \
            -backend-config="path={self.state_file_path}" \
            -input=false \
            -no-color
        """.strip()
        return self._run_tf_command(cmd)

    def apply(self, vars: dict = None, destroy: bool = False) -> TFResult:
        var_args = ""
        if vars:
            for k, v in vars.items():
                var_args += f' -var="{k}={v}"'

        destroy_flag = "-destroy" if destroy else ""

        cmd = f"""
        terraform apply \
            {destroy_flag} \
            -auto-approve \
            -input=false \
            {var_args} \
            -no-color
        """.strip()
        return self._run_tf_command(cmd)

    def destroy(self, vars: dict = None) -> TFResult:
        return self.apply(vars=vars, destroy=True)

    def output(self) -> dict[str, Any]:
        cmd = f"""
        terraform output \
            -json \
            -no-color
        """.strip()
        rc, stdout, stderr = self._run_raw_command(cmd)
        if rc != 0:
            raise Exception(f"Terraform output failed: {stderr}")
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            raise Exception(f"Terraform output JSON decode failed: {stdout}")
