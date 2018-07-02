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
output "sdk.lambda_role" {value = "${aws_iam_role.lambda_exec_role.arn}"}
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
