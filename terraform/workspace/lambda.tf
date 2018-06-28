resource "aws_lambda_alias" "check_task_alias" {
  name             = "${terraform.workspace}"
  description      = "Alias to function by version"
  function_name    = "${data.terraform_remote_state.common.check_task.arn}"
  function_version = "${data.terraform_remote_state.common.check_task.version}"
}

resource "aws_lambda_alias" "run_task_alias" {
  name             = "${terraform.workspace}"
  description      = "Alias to function by version"
  function_name    = "${data.terraform_remote_state.common.run_task.arn}"
  function_version = "${data.terraform_remote_state.common.run_task.version}"
}

resource "aws_lambda_alias" "call_api_alias" {
  name             = "${terraform.workspace}"
  description      = "Alias to function by version"
  function_name    = "${data.terraform_remote_state.common.call_api.arn}"
  function_version = "${data.terraform_remote_state.common.call_api.version}"
}

resource "aws_lambda_alias" "send_sns_alias" {
  name             = "${terraform.workspace}"
  description      = "Alias to function by version"
  function_name    = "${data.terraform_remote_state.common.send_sns.arn}"
  function_version = "${data.terraform_remote_state.common.send_sns.version}"
}
