module "lambda-package" {
  source = "github.com/compassmarketing/terraform-package-lambda"
  path = "./lambdas"
  requirements = "requirements.txt"
}

# Check SDK Task
resource "aws_lambda_function" "check_task" {
  function_name     = "${terraform.workspace}-drench-sdk-check-task"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "check_task.handler"
  runtime           = "python3.6"
  publish           = true
}
# Run SDK Task
resource "aws_lambda_function" "run_task" {
  function_name     = "${terraform.workspace}-drench-sdk-run-task"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "run_task.handler"
  runtime           = "python3.6"
  publish           = true
}

# Stop SDK Task
resource "aws_lambda_function" "stop_task" {
  function_name     = "${terraform.workspace}-drench-sdk-stop-task"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "stop_task.handler"
  runtime           = "python3.6"
  publish           = true
}

# Send SNS
resource "aws_lambda_function" "send_sns" {
  function_name     = "${terraform.workspace}-drench-sdk-send-sns"
  filename          = "${module.lambda-package.output_filename}"
  source_code_hash  = "${module.lambda-package.output_base64sha256}"
  role              = "${data.terraform_remote_state.common.sdk.lambda_role}"
  handler           = "send_sns.handler"
  runtime           = "python3.6"
  publish           = true
}
