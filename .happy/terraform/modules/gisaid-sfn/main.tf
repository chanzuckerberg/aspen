locals {
  # TODO -- hardcoded mapping of sfn generic names to specific names for rdev isn't gonna work forever.
  lambdas = {
    "preprocess-input" = "swipe-aspen-rdev-preprocess-input"
    "process-stage-output" = "swipe-aspen-rdev-process-stage-output"
    "handle-success" = "swipe-aspen-rdev-handle-success"
    "handle-failure" = "swipe-aspen-rdev-handle-failure"
    "swipe-process-batch-event" = "swipe-aspen-rdev-swipe-aspen-rdev-process-batch-event"
    "swipe-process-sfn-event" = "swipe-aspen-rdev-swipe-aspen-rdev-process-sfn-event"
    "report_metrics" = "swipe-aspen-rdev-report_metrics"
    "report_spot_interruption" = "swipe-aspen-rdev-report_spot_interruption"
  }
  sfn_def = yamldecode(templatefile("${path.module}/sfn.yml", merge(local.lambdas, {
    deployment_environment = "aspen-rdev" # FIXME
    deployment_stage = var.deployment_stage
    remote_dev_prefix = var.stack_resource_prefix
    aws_default_region = "us-west-2"
    batch_ec2_job_queue_name = var.ec2_queue_arn
    batch_spot_job_queue_name = var.spot_queue_arn
    batch_job_definition_name = var.job_definition_name
  })))
  jobs = {
    "Ingest" = {
      "memory" = 1024
      "vcpus" = 1
      "next" = "transform"
    }
    "Transform" = {
      "memory" = 1024
      "vcpus" = 1
      "next" = "align"
    }
    "Align" = {
      "memory" = 1024
      "vcpus" = 1
      "end" = true
    }
  }
  # Make a copy of our desired states
  states = local.sfn_def["States"]
  # Make a copy for each job, but make the ends of each job point to the next.
  new_states = merge(flatten([ for jobname, conf in local.jobs: [
    for statename, state in local.states: {
    join("", [jobname, statename]) = merge(state, {
      "End": lookup(state, "End", false) ? try(join("", [jobname, conf["next"]]), true) : false
      "Next": coalesce(
      lookup(state, "Next", "") == "HandleFailure" ? "HandleFailure" : null, # HandleFailure is always an end state
      lookup(state, "End", false) ? try(join("", [jobname, conf["next"]]), null) : null, # If this was an end state, send it to the next job
      "${jobname}${statename}") # Send it to the next state within this job. FIXME this isn't handling the case where we need to actually end at the last HandleSuccess.
    })} if statename != "HandleFailure"
  ]])...)
  new_sfn = {
    "Comment" = local.sfn_def["Comment"]
    "StartAt" = "IngestPreprocessInput"
    "TimeoutSeconds" = local.sfn_def["TimeoutSeconds"]
    "States" = merge(local.new_states, {"HandleFailure": local.states["HandleFailure"]})
  }
}
resource "aws_sfn_state_machine" "state_machine" {
  name     = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.app_name}-sfn"
  role_arn = var.role_arn

  definition = jsonencode(local.new_sfn)

}

resource aws_cloudwatch_log_group cloud_watch_logs_group {
  retention_in_days = 365
  name              = "/${var.stack_resource_prefix}/${var.deployment_stage}/${var.custom_stack_name}/${var.app_name}-sfn"
}
