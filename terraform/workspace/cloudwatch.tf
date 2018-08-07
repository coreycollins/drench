resource "aws_cloudwatch_event_rule" "stop_event" {
  name        = "${terraform.workspace}-drench-sdk-stop"
  description = "Stop long running task if cancel event received"

  event_pattern = <<PATTERN
  {
    "source": [
      "aws.states"
    ],
    "detail-type": [
      "AWS API Call via CloudTrail"
    ],
    "detail": {
      "eventSource": [
        "states.amazonaws.com"
      ],
      "eventName": [
        "StopExecution"
      ]
    }
  }
PATTERN
}

resource "aws_cloudwatch_event_target" "stop-task" {
  rule      = "${aws_cloudwatch_event_rule.stop_event.name}"
  arn       = "${aws_lambda_function.stop_task.arn}"
}
