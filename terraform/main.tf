variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}

terraform {
  backend "s3" {
    bucket = "infra.compass.com"
    region = "us-east-1"
    key    = "statemachine/state"
    workspace_key_prefix = "compass"
  }
}

provider "aws" {
  access_key    = "${var.aws_access_key}"
  secret_key    = "${var.aws_secret_key}"
  region        = "${var.aws_region}"
}

data "terraform_remote_state" "core" {
  backend = "s3"
  config {
    bucket = "infra.compass.com"
    key    = "compass/production/core/state"
    region = "us-east-1"
  }
}

# Batch Job Status Check
resource "aws_lambda_function" "check_batch" {
  function_name     = "${terraform.workspace}-check_batch"
  filename          = "build/lambda_functions.zip"
  source_code_hash  = "${base64sha256(file("build/lambda_functions.zip"))}"
  role              = "${data.terraform_remote_state.core.aws_iam_lambda_exec_role}"
  handler           = "check_batch.handler"
  runtime           = "python2.7"
}
output "aws_lambda_check_batch" {
  value = "${aws_lambda_function.check_batch.arn}"
}

# Run Batch Job
resource "aws_lambda_function" "run_batch" {
  function_name     = "${terraform.workspace}-run_batch"
  filename          = "build/lambda_functions.zip"
  source_code_hash  = "${base64sha256(file("build/lambda_functions.zip"))}"
  role              = "${data.terraform_remote_state.core.aws_iam_lambda_exec_role}"
  handler           = "run_batch.handler"
  runtime           = "python2.7"
}
output "aws_lambda_run_batch" {
  value = "${aws_lambda_function.run_batch.arn}"
}


# Glue Job Status Check
resource "aws_lambda_function" "check_glue" {
  function_name     = "${terraform.workspace}-check_glue"
  filename          = "build/lambda_functions.zip"
  source_code_hash  = "${base64sha256(file("build/lambda_functions.zip"))}"
  role              = "${data.terraform_remote_state.core.aws_iam_lambda_exec_role}"
  handler           = "check_glue.handler"
  runtime           = "python2.7"
}
output "aws_lambda_check_glue" {
  value = "${aws_lambda_function.check_glue.arn}"
}

# Run Glue Job
resource "aws_lambda_function" "run_glue" {
  function_name     = "${terraform.workspace}-run_glue"
  filename          = "build/lambda_functions.zip"
  source_code_hash  = "${base64sha256(file("build/lambda_functions.zip"))}"
  role              = "${data.terraform_remote_state.core.aws_iam_lambda_exec_role}"
  handler           = "run_glue.handler"
  runtime           = "python2.7"
}
output "aws_lambda_run_glue" {
  value = "${aws_lambda_function.run_glue.arn}"
}


# Send SNS Message
resource "aws_lambda_function" "send_sns" {
  function_name     = "${terraform.workspace}-send_sns"
  filename          = "build/lambda_functions.zip"
  source_code_hash  = "${base64sha256(file("build/lambda_functions.zip"))}"
  role              = "${data.terraform_remote_state.core.aws_iam_lambda_exec_role}"
  handler           = "send_sns.handler"
  runtime           = "python2.7"
}
output "aws_lambda_send_sns" {
  value = "${aws_lambda_function.send_sns.arn}"
}
