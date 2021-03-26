# This is a batch job
#

data aws_region current {}

resource aws_batch_job_definition batch_job_def {
  type = "container"
  name = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.app_name}"
  container_properties = <<EOF
{
  "jobRoleArn": "${var.batch_role_arn}",
  "image": "${var.image}",
  "memory": 28000,
  "environment": [
    {
      "name": "DEPLOYMENT_STAGE",
      "value": "${var.deployment_stage}"
    },
    {
      "name": "AWS_DEFAULT_REGION",
      "value": "${data.aws_region.current.name}"
    },
    {
      "name": "REMOTE_DEV_PREFIX",
      "value": "${var.remote_dev_prefix}"
    },
    {
      "name": "FRONTEND_URL",
      "value": "${var.frontend_url}"
    }
  ],
  "vcpus": 2,
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "${aws_cloudwatch_log_group.cloud_watch_logs_group.id}",
      "awslogs-region": "${data.aws_region.current.name}"
    }
  }
}
EOF
}

resource aws_cloudwatch_log_group cloud_watch_logs_group {
  retention_in_days = 365
  name              = "/${var.stack_resource_prefix}/${var.deployment_stage}/${var.custom_stack_name}/${var.app_name}"
}
