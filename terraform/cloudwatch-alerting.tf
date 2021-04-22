variable "log_group_subscription_filters" {

}

resource "aws_secretsmanager_secret" "slack_oauth_token" {
  name                    = var.slack_oauth_token_secret_name
  recovery_window_in_days = 0
}

resource "aws_cloudwatch_log_subscription_filter" "cloudwatch_alerting" {
  for_each        = var.log_group_subscription_filters
  name            = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.name}-${each.key}"
  log_group_name  = each.key
  filter_pattern  = each.value
  destination_arn = aws_lambda_function.cloudwatch_alerting.arn
}
