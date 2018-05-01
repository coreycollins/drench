variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}

terraform {
  backend "s3" {
    bucket = "infra.compass.com"
    region = "us-east-1"
    key    = "drench_sdk/production/state"
  }
}

provider "aws" {
  access_key    = "${var.aws_access_key}"
  secret_key    = "${var.aws_secret_key}"
  region        = "${var.aws_region}"
}

module "alias" {
  source = "../modules"
  alias  = "v1"
}
