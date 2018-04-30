variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}

terraform {
  backend "s3" {
    bucket = "infra.compass.com"
    region = "us-east-1"
    key    = "drench_sdk/development/state"
  }
}

provider "aws" {
  access_key    = "${var.aws_access_key}"
  secret_key    = "${var.aws_secret_key}"
  region        = "${var.aws_region}"
}

module "alias" {
	source				= "../modules"
  aws_access_key    = "${var.aws_access_key}"
  aws_secret_key    = "${var.aws_secret_key}"
  aws_region        = "${var.aws_region}"
	alias					= "canary"
}
