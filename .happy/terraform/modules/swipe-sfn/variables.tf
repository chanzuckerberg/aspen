variable app_name {
  type        = string
  description = "Application name"
}

variable stack_resource_prefix {
  type        = string
  description = "Prefix for account-level resources"
}

variable remote_dev_prefix {
  type        = string
  description = "Remote Dev namespace (db schema prefix)"
  default     = ""
}

variable job_definition_name {
  type        = string
  description = "Name of the batch job definition"
}

variable ec2_queue_arn {
  type        = string
  description = "ARN of the batch job queue"
}

variable spot_queue_arn {
  type        = string
  description = "ARN of the batch job queue"
}

variable role_arn {
  type        = string
  description = "ARN for the role assumed by tasks"
}

variable custom_stack_name {
  type        = string
  description = "Please provide the stack name"
}

variable deployment_stage {
  type        = string
  description = "The name of the deployment stage of the Application"
  default     = "dev"
}
