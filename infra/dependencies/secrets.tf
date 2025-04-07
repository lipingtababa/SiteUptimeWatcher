# This file is intentionally left empty as we're now using Aiven PostgreSQL
# and storing the connection details in SSM parameters defined in aiven-postgres.tf


variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_account" {
  type    = string
  default = "954976318202"
}
