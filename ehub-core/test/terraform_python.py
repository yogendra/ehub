import os
from python_terraform import Terraform

__location__ = os.path.dirname(os.path.abspath(__file__))
tf_base = os.path.join(__location__, "tf")


def output_test():
    tf_dir = os.path.join(tf_base, "output-test")
    tf = Terraform(working_dir=tf_dir)
    tf.init()
    tf.apply(skip_plan=True)

    output = tf.output()
    print(output)
    print("some_id:", output["some_id"])
    print("some_id.value:", output["some_id"]["value"])
    print("missing_value:", output.get("missing_value", {"value": ""})["value"])


if __name__ == "__main__":
    output_test()
