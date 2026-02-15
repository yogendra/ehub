import sys
import os
import logging

# Import TFWrapper from main.py in the same directory
from main import TFWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_terraform_pass():
    state_file_rel = "tf_wrapper_test_terraform_pass.tfstate"

    tf = TFWrapper(working_dir="tf_test_wrapper", state_file_path=state_file_rel)

    print("--- Starting Terraform Init ---")
    result = tf.init()
    if result.rc != 0:
        print(f"Init failed with code {result.rc}")
        print(f"Stderr: {result.stderr}")
        sys.exit(1)
    print("Init successful")

    print("\n--- Starting Terraform Apply ---")
    vars = {"file_prefix": "tf_test_wrapper_t1"}
    result = tf.apply(vars=vars)
    if result.rc != 0:
        print(f"Apply failed with code {result.rc}")
        print(f"Stderr: {result.stderr}")
        sys.exit(1)
    print("Apply successful")

    print("\n--- Checking Outputs ---")
    outputs = result.output
    file_path = outputs.get("file_path", {}).get("value")
    print(f"Created file path: {file_path}")

    if not file_path or not os.path.exists(file_path):
        print("Error: File was not created or output not found")
        sys.exit(1)

    with open(file_path, "r") as f:
        content = f.read()
        print(f"File content: {content}")
        if content != "Hello from Terraform!":
            print("Error: File content mismatch")
            sys.exit(1)

    print("\n--- Starting Terraform Destroy ---")
    result = tf.destroy(vars=vars)
    if result.rc != 0:
        print(f"Destroy failed with code {result.rc}")
        sys.exit(1)
    print("Destroy successful")

    if os.path.exists(file_path):
        print("Error: File still exists after destroy")
    else:
        print("File successfully deleted by Terraform")

    print("\nTest passed successfully!")


def test_terraform_failure():
    print("\n--- Starting Failure Test (Missing Variable) ---")
    tf = TFWrapper(
        working_dir="tf_test_wrapper",
        state_file_path="tf_wrapper_test_terraform_fail.tfstate",
    )
    tf.init()

    # This should fail because 'file_prefix' is required
    result = tf.apply(vars={})
    if result.rc != 0:
        print(f"Success: Apply failed as expected with code {result.rc}")
        # print(f"Error message: {result.stderr}")
    else:
        print("Error: Apply succeeded unexpectedly")
        sys.exit(1)


if __name__ == "__main__":
    test_terraform_pass()
    test_terraform_failure()
