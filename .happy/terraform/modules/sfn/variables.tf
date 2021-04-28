variable app_name {
  type        = string
  description = "Application name"
}

variable stack_resource_prefix {
  type        = string
  description = "Prefix for account-level resources"
}

variable job_definition_name {
  type        = string
  description = "Name of the batch job definition"
}

variable ec2_queue_arn {
  type        = string
  description = "ARN of the batch job queue"
}

variable lambda_success_handler {
  type        = string
  description = "Function name for the Lambda success handler"
}

variable lambda_error_handler {
  type        = string
  description = "Function name for the Lambda error handler"
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
