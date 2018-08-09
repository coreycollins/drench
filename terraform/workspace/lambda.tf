module "lambda-package" {
  source = "github.com/compassmarketing/terraform-package-lambda"
  path = "./lambdas"
  requirements = "requirements.txt"
  build_dir    = "/tmp"
}

# Check SDK Task
resource "aws_lambda_function" "check_task" {
  function_name     = "${terraform.workspace}-drench-sdk-check-task"
  filename          = "${module.lambda-package.output_filename}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "check_task.handler"
  runtime           = "python3.6"
  publish           = true
}
# Run SDK Task
resource "aws_lambda_function" "run_task" {
  function_name     = "${terraform.workspace}-drench-sdk-run-task"
  filename          = "${module.lambda-package.output_filename}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "run_task.handler"
  runtime           = "python3.6"
  publish           = true
}

# Stop SDK Task
resource "aws_lambda_function" "stop_task" {
  function_name     = "${terraform.workspace}-drench-sdk-stop-task"
  filename          = "${module.lambda-package.output_filename}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "stop_task.handler"
  runtime           = "python3.6"
  publish           = true
}

# Allow cloudwatch event to trigger stop task
resource "aws_lambda_permission" "allow_cloudwatch_stop" {
  statement_id   = "AllowExecutionFromCloudWatch"
  action         = "lambda:InvokeFunction"
  function_name  = "${aws_lambda_function.stop_task.function_name}"
  principal      = "events.amazonaws.com"
  source_arn     = "${aws_cloudwatch_event_rule.stop_event.arn}"
}

# Send SNS
resource "aws_lambda_function" "send_sns" {
  function_name     = "${terraform.workspace}-drench-sdk-send-sns"
  filename          = "${module.lambda-package.output_filename}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "send_sns.handler"
  runtime           = "python3.6"
  publish           = true
}
