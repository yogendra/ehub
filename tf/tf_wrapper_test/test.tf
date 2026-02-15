terraform {
  backend "local" {}
}

variable "file_prefix" {
  type = string
}

resource "local_file" "example" {
  content  = "Hello from Terraform!"
  filename = "${path.module}/${var.file_prefix}_example.txt"
}

output "file_path" {
  value = abspath(local_file.example.filename)
}
