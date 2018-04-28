variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {}

variable "version" {}

terraform {
  backend "s3" {
    bucket = "infra.compass.com"
    region = "us-east-1"
    key    = "drench_sdk/state"
    workspace_key_prefix = "compass"
  }
}

provider "aws" {
  access_key    = "${var.aws_access_key}"
  secret_key    = "${var.aws_secret_key}"
  region        = "${var.aws_region}"
}

module "lambda-package" {
  source = "github.com/compassmarketing/terraform-package-lambda"
  path = "lambdas"

  /* Optional, defaults to the value of $code, except the extension is
   * replaced with ".zip" */
  output_filename = "lambda_functions.zip"

  /* Optional, specifies additional files to include.  These are relative
   * to the location of the code. */
  # extra_files = [ "data-file.txt", "extra-dir" ]
}

# Check SDK Task
resource "aws_lambda_function" "check_task" {
  function_name     = "drench-sdk-check-task"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${aws_iam_role.lambda_exec_role.arn}"
  handler           = "check_task.handler"
  runtime           = "python3.6"
  publish           = true
}

resource "aws_lambda_alias" "check_task_alias" {
  name             = "${var.version}"
  description      = "Alias to function by version"
  function_name    = "${aws_lambda_function.check_task.arn}"
  function_version = "${aws_lambda_function.check_task.version}"
}

# Run SDK Task
resource "aws_lambda_function" "run_task" {
  function_name     = "drench-sdk-run-task"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${aws_iam_role.lambda_exec_role.arn}"
  handler           = "run_task.handler"
  runtime           = "python3.6"
  publish           = true
}

resource "aws_lambda_alias" "run_task_alias" {
  name             = "${var.version}"
  description      = "Alias to function by version"
  function_name    = "${aws_lambda_function.run_task.arn}"
  function_version = "${aws_lambda_function.run_task.version}"
}

# Call API
resource "aws_lambda_function" "call_api" {
  function_name     = "drench-sdk-call-api"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${aws_iam_role.lambda_exec_role.arn}"
  handler           = "call_api.handler"
  runtime           = "python3.6"
  publish           = true
}

resource "aws_lambda_alias" "call_api_alias" {
  name             = "${var.version}"
  description      = "Alias to function by version"
  function_name    = "${aws_lambda_function.call_api.arn}"
  function_version = "${aws_lambda_function.call_api.version}"
}

# Send SNS
resource "aws_lambda_function" "send_sns" {
  function_name     = "drench-sdk-send-sns"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${aws_iam_role.lambda_exec_role.arn}"
  handler           = "send_sns.handler"
  runtime           = "python3.6"
  publish           = true
}

resource "aws_lambda_alias" "send_sns_alias" {
  name             = "${var.version}"
  description      = "Alias to function by version"
  function_name    = "${aws_lambda_function.send_sns.arn}"
  function_version = "${aws_lambda_function.send_sns.version}"
}

##
## Lambda Execute Role
##
resource "aws_iam_role" "lambda_exec_role" {
  name = "drench-sdk-lambda-exec-role"
  path = "/"

  assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "sts:AssumeRole",
            "Principal": {
               "Service": "lambda.amazonaws.com"
            },
            "Effect": "Allow",
            "Sid": ""
        }
    ]
}
EOF
}

# Default Lambda Execution Policy
resource "aws_iam_role_policy_attachment" "lambda_default_attach" {
    role       = "${aws_iam_role.lambda_exec_role.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_exec_policy" {
    name        = "drench-sdk-lambda-exec-policy"
    description = "Permmisson for lambda execution"
    policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
        "Effect": "Allow",
        "Action": [
            "sqs:*",
            "batch:*",
            "sns:*",
            "s3:*",
            "states:*",
            "athena:*",
            "glue:*",
            "lambda:*"
        ],
        "Resource": "*"
    }
  ]
}
EOF
}


resource "aws_iam_role_policy_attachment" "lambda_exec_policy" {
    role       = "${aws_iam_role.lambda_exec_role.name}"
    policy_arn = "${aws_iam_policy.lambda_exec_policy.arn}"
}
