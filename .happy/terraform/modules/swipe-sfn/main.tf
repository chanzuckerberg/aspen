locals {
  env = "${var.stack_resource_prefix}-${var.deployment_stage}"
  lambda_env = "swipe-${var.stack_resource_prefix}-${var.deployment_stage}"

  # TODO, we should probably import this map from somewhere instead of hardcoding it.
  lambdas = {
    "preprocess-input" = "${local.lambda_env}-preprocess-input"
    "process-stage-output" = "${local.lambda_env}-process-stage-output"
    "handle-success" = "${local.lambda_env}-handle-success"
    "handle-failure" = "${local.lambda_env}-handle-failure"
    "swipe-process-batch-event" = "${local.lambda_env}-${local.lambda_env}-process-batch-event"
    "swipe-process-sfn-event" = "${local.lambda_env}-${local.lambda_env}-process-sfn-event"
    "report_metrics" = "${local.lambda_env}-report_metrics"
    "report_spot_interruption" = "${local.lambda_env}-report_spot_interruption"
  }
  sfn_def = yamldecode(templatefile("${path.module}/sfn.yml", merge(local.lambdas, {
    deployment_environment = local.env
    deployment_stage = var.deployment_stage
    remote_dev_prefix = var.remote_dev_prefix
    aws_default_region = "us-west-2" # FIXME hardcoded
    batch_ec2_job_queue_name = var.ec2_queue_arn
    batch_spot_job_queue_name = var.spot_queue_arn
    batch_job_definition_name = var.job_definition_name
    memory = 420000
    vcpus = 1
  })))
}
resource "aws_sfn_state_machine" "state_machine" {
  name     = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.app_name}-sfn"
  role_arn = var.role_arn

  definition = jsonencode(local.sfn_def)

}

resource aws_cloudwatch_log_group cloud_watch_logs_group {
  retention_in_days = 365
  name              = "/${var.stack_resource_prefix}/${var.deployment_stage}/${var.custom_stack_name}/${var.app_name}-sfn"
}
