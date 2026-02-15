from dataclasses import dataclass
from typing import Any
import subprocess
import os
import json
import logging
import shutil
import tempfile

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
        self.source_dir = os.path.abspath(os.path.join(tf_root, working_dir))
        if not os.path.exists(self.source_dir):
            raise ValueError(f"Source directory does not exist: {self.source_dir}")

        # Create state directory
        state_dir = os.path.join(state_dir_root, f"{working_dir}/{state_file_path}")
        os.makedirs(state_dir, exist_ok=True)
        self.state_file_path = os.path.join(state_dir, "terraform.tfstate")

        # Create ephemeral working directory
        self.working_dir = tempfile.mkdtemp(
            prefix=f"tf-{working_dir.replace('/', '-')}-"
        )
        logger.debug(f"Created ephemeral working directory: {self.working_dir}")

        # Copy source files to the temporary execution directory
        for item in os.listdir(self.source_dir):
            if item.startswith(".") or item == "test":  # Skip hidden and test dirs
                continue
            s = os.path.join(self.source_dir, item)
            d = os.path.join(self.working_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
            elif os.path.isdir(s):
                shutil.copytree(s, d)

    def cleanup(self):
        """Removes the ephemeral working directory."""
        if hasattr(self, "working_dir") and os.path.exists(self.working_dir):
            logger.debug(f"Cleaning up ephemeral directory: {self.working_dir}")
            shutil.rmtree(self.working_dir)

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

    def _run_tf_command(self, cmd: str, capture_output: bool = True) -> TFResult:
        rc, stdout, stderr = self._run_raw_command(cmd)
        output_data = {}
        if rc == 0 and capture_output:
            try:
                output_data = self.output()
            except Exception as e:
                logger.debug(f"Terraform output skipped or failed: {e}")
        return TFResult(rc=rc, stdout=stdout, stderr=stderr, output=output_data)

    def init(self) -> TFResult:
        cmd = f"""
        terraform init \
            -reconfigure \
            -backend-config="path={self.state_file_path}" \
            -input=false \
            -no-color
        """.strip()
        return self._run_tf_command(cmd, capture_output=False)

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
        # Check if state file exists before trying to get output
        if not os.path.exists(self.state_file_path):
            logger.debug(
                f"State file {self.state_file_path} does not exist. Returning empty output."
            )
            return {}

        cmd = f"""
        terraform output \
            -json \
            -no-color
        """.strip()
        rc, stdout, stderr = self._run_raw_command(cmd)
        if rc != 0:
            # It's possible there are just no outputs defined
            if "no outputs" in stderr.lower():
                return {}
            raise Exception(f"Terraform output failed: {stderr}")
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            if not stdout.strip():
                return {}
            raise Exception(f"Terraform output JSON decode failed: {stdout}")
