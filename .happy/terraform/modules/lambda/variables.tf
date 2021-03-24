variable stack_resource_prefix {
  type        = string
  description = "Prefix for account-level resources"
}

variable image {
  type        = string
  description = "Image name"
}

variable name {
  type        = string
  description = "Lambda name"
}

variable custom_stack_name {
  type        = string
  description = "Please provide the stack name"
}

variable remote_dev_prefix {
  type        = string
  description = "S3 storage path / db schema prefix"
  default     = ""
}

variable deployment_stage {
  type        = string
  description = "The name of the deployment stage of the Application"
}

variable lambda_execution_role {
  type        = string
  description = "Role for lambda execution"
}

variable security_groups {
  type        = list(string)
  description = "Security groups for lambda tasks"
}

variable subnets {
  type        = list(string)
  description = "Subnets for lambda tasks"
}
