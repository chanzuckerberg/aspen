resource "aws_iam_role" "cloudwatch-batch-trigger-role" {
  name = "cloudwatch-batch-trigger-role"
  assume_role_policy = templatefile("${path.module}/iam_templates/trust_policy.json", {
    trust_services = ["events"]
  })
}


resource "aws_iam_role_policy_attachment" "cloudwatch-can-trigger-batch-jobs" {
  role       = aws_iam_role.cloudwatch-batch-trigger-role.name
  policy_arn = aws_iam_policy.can-submit-aspen-batch-job.arn
}


resource "aws_cloudwatch_event_rule" "ingest-gisaid-rule" {
  name                = "ingest-gisaid"
  description         = "Ingest GISAID data daily"
  schedule_expression = "cron(0 0 ? * 1-5 *)"
}


resource "aws_cloudwatch_event_target" "ingest-gisaid-target" {
  target_id = "ingest-gisaid-target"
  rule      = aws_cloudwatch_event_rule.ingest-gisaid-rule.name
  arn       = aws_batch_job_queue.aspen-batch-job-queue.arn
  role_arn  = aws_iam_role.cloudwatch-batch-trigger-role.arn

  batch_target {
    job_name       = "ingest-gisaid"
    job_definition = aws_batch_job_definition.aspen-batch-job-definition.name
  }

  # These are overrides to the defaults specified in the job definition.  See
  # https://docs.aws.amazon.com/batch/latest/APIReference/API_ContainerOverrides.html
  # for more details.
  input = <<-CONTAINER_OVERRIDES
  {
    "ContainerOverrides": {
      "Command": [
        "trunk",
        "src/backend/aspen/workflows/ingest_gisaid/ingest.sh"
      ]
    }
  }
  CONTAINER_OVERRIDES
}


resource "aws_cloudwatch_event_rule" "update-czb-gisaid-rule" {
  name                = "update-czb-gisaid-rule"
  description         = "Ingest GISAID data daily"
  schedule_expression = "cron(0 1 ? * 1-5 *)"
}


resource "aws_cloudwatch_event_target" "update-czb-gisaid-target" {
  target_id = "update-czb-gisaid-target"
  rule      = aws_cloudwatch_event_rule.update-czb-gisaid-rule.name
  arn       = aws_batch_job_queue.aspen-batch-job-queue.arn
  role_arn  = aws_iam_role.cloudwatch-batch-trigger-role.arn

  batch_target {
    job_name       = "update-czb-gisaid"
    job_definition = aws_batch_job_definition.aspen-batch-job-definition.name
  }

  # These are overrides to the defaults specified in the job definition.  See
  # https://docs.aws.amazon.com/batch/latest/APIReference/API_ContainerOverrides.html
  # for more details.
  input = <<-CONTAINER_OVERRIDES
  {
    "ContainerOverrides": {
      "Command": [
        "trunk",
        "src/backend/aspen/workflows/update_czb_gisaid/update.sh"
      ]
    }
  }
  CONTAINER_OVERRIDES
}
