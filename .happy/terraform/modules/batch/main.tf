# This is a batch job
#

data aws_region current {}

locals {
  container_properties = yamldecode(templatefile("${path.module}/container_properties.yml", {
    app_name           = var.app_name,
    batch_docker_image = "473004499091.dkr.ecr.us-west-2.amazonaws.com/aspen-swipe:branch-main" # FIXME
    aws_region         = data.aws_region.current.name,
    batch_job_role_arn = var.batch_role_arn
    deployment_stage   = var.deployment_stage
    deployment_environment = "aspen-rdev"
    remote_dev_prefix  = var.remote_dev_prefix
    frontend_url       = var.frontend_url
    log_group          = aws_cloudwatch_log_group.cloud_watch_logs_group.name
  }))
}


resource aws_batch_job_definition batch_job_def {
  type = "container"
  name = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.app_name}"

  container_properties = jsonencode(local.container_properties)
}

resource aws_cloudwatch_log_group cloud_watch_logs_group {
  retention_in_days = 365
  name              = "/${var.stack_resource_prefix}/${var.deployment_stage}/${var.custom_stack_name}/${var.app_name}"
}
