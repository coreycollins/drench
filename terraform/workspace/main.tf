variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {
  default = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "infra.compass.com"
    region = "us-east-1"
    key    = "drench_sdk/workspace"
  }
}

provider "aws" {
  access_key    = "${var.aws_access_key}"
  secret_key    = "${var.aws_secret_key}"
  region        = "${var.aws_region}"
}

data "terraform_remote_state" "common" {
  backend = "s3"
  config {
    bucket = "infra.compass.com"
    key    = "drench_sdk/common/state" // FIXME
    region = "us-east-1"
  }
}
