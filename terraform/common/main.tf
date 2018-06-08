variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {
  default = "us-east-1"
}

terraform {
  backend "s3" {
    bucket = "infra.compass.com"
    region = "us-east-1"
    key    = "drench_sdk/common/state"
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
  deps_filename = "lib/dependencies.zip"

  /* Optional, defaults to the value of $code, except the extension is
   * replaced with ".zip" */
  output_filename = "lambda_functions.zip"
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
output "check_task.version" {value = "${aws_lambda_function.check_task.version}"}
output "check_task.arn" {value = "${aws_lambda_function.check_task.arn}"}

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
output "run_task.version" {value = "${aws_lambda_function.run_task.version}"}
output "run_task.arn" {value = "${aws_lambda_function.run_task.arn}"}

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
output "call_api.version" {value = "${aws_lambda_function.call_api.version}"}
output "call_api.arn" {value = "${aws_lambda_function.call_api.arn}"}

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
output "send_sns.version" {value = "${aws_lambda_function.send_sns.version}"}
output "send_sns.arn" {value = "${aws_lambda_function.send_sns.arn}"}

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


data "aws_iam_policy_document" "sns-topic-policy" {
  policy_id = "__default_policy_ID"

  statement {
    actions = [
      "SNS:Publish",
    ]

    effect = "Allow"

    resources = [
      "arn:aws:sns:${var.aws_region}:909533743566:*"
    ]

    condition {
          test     = "ArnLike"
          variable = "aws:SourceArn"
          values = ["arn:aws:*:${var.aws_region}:909533743566:*"]
    }

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }
    sid = "__console_sub_0"
  }
}

resource "aws_sns_topic" "sdk_workflow_deathrattle" {
  name = "drench-sdk-sfn-fail-${terraform.workspace}"
  policy = "${data.aws_iam_policy_document.sns-topic-policy.json}"
}
