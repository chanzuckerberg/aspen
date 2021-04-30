locals {
  # TODO -- hardcoded mapping of sfn generic names to specific names for rdev isn't gonna work forever.
  lambdas = {
    "preprocess-input" = {
      "function_name" = "swipe-aspen-rdev-preprocess-input",
    }
    "process-stage-output" = {
      "function_name" = "swipe-aspen-rdev-process-stage-output",
    }
    "handle-success" = {
      "function_name" = "swipe-aspen-rdev-handle-success",
    }
    "handle-failure" = {
      "function_name" = "swipe-aspen-rdev-handle-failure",
    }
    "swipe-process-batch-event" = {
      "function_name" = "swipe-aspen-rdev-swipe-aspen-rdev-process-batch-event",
    }
    "swipe-process-sfn-event" = {
      "function_name" = "swipe-aspen-rdev-swipe-aspen-rdev-process-sfn-event",
    }
    "report_metrics" = {
      "function_name" = "swipe-aspen-rdev-report_metrics",
    }
    "report_spot_interruption" = {
      "function_name" = "swipe-aspen-rdev-report_spot_interruption",
    }
  }
}
resource "aws_sfn_state_machine" "state_machine" {
  name     = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.app_name}-sfn"
  role_arn = var.role_arn

  definition = jsonencode(yamldecode(templatefile("${path.module}/sfn.yml", {
    lambdas = local.lambdas
    batch_ec2_job_queue_name = var.ec2_queue_arn
    batch_job_definition_name = var.job_definition_name
  })))

}

resource aws_cloudwatch_log_group cloud_watch_logs_group {
  retention_in_days = 365
  name              = "/${var.stack_resource_prefix}/${var.deployment_stage}/${var.custom_stack_name}/${var.app_name}-sfn"
}
