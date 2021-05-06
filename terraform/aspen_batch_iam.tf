data "aws_secretsmanager_secret" "aspen_config" {
  name = "aspen-config"
}

data "aws_secretsmanager_secret" "gisaid-download-credentials" {
  name = "gisaid-download-credentials"
}

data "aws_secretsmanager_secret" "czb-aws-access" {
  name = "czb-aws-access"
}

resource "aws_iam_role" "aspen-batch-jobs-role" {
  name = "aspen-batch-jobs-role"
  assume_role_policy = templatefile("${path.module}/iam_templates/trust_policy.json", {
    trust_services = ["ecs-tasks"]
  })
}


# this policy is applied to any role who can submit a job to aspen batch.
resource "aws_iam_policy" "can-submit-aspen-batch-job" {
  name = "can-submit-aspen-batch-job"
  policy = <<-POLICY
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": [
                  "batch:SubmitJob"
              ],
              "Resource": [
                  "arn:aws:batch:*:*:job-definition/${aws_batch_job_definition.aspen-batch-job-definition.name}",
                  "arn:aws:batch:*:*:job-queue/${aws_batch_job_queue.aspen-batch-job-queue.name}"
              ]
          }
      ]
  }
  POLICY
}


# these additional policies are applied to the role given to jobs running in the aspen batch pipeline.
resource "aws_iam_policy" "aspen-batch-jobs-policies" {
  name = "aspen-batch-jobs-policies"
  policy = <<-POLICY
  {
      "Version": "2012-10-17",
      "Statement": [
          {
              "Effect": "Allow",
              "Action": "secretsmanager:GetSecretValue",
              "Resource": [
                  "${data.aws_secretsmanager_secret.aspen_config.arn}",
                  "${data.aws_secretsmanager_secret.gisaid-download-credentials.arn}",
                  "${data.aws_secretsmanager_secret.czb-aws-access.arn}"
              ]
          },
          {
              "Effect": "Allow",
              "Action": "rds:DescribeDBInstances",
              "Resource": [
                  "${aws_db_instance.db.arn}"
              ]
          },
          {
              "Effect": "Allow",
              "Action": [
                  "s3:GetObject",
                  "s3:PutObject"
              ],
              "Resource": [
                  "arn:aws:s3:::${aws_s3_bucket.aspen-db-data.bucket}/raw_gisaid_dump/*",
                  "arn:aws:s3:::${aws_s3_bucket.aspen-db-data.bucket}/processed_gisaid_dump/*",
                  "arn:aws:s3:::${aws_s3_bucket.aspen-db-data.bucket}/aligned_gisaid_dump/*",
                  "arn:aws:s3:::${aws_s3_bucket.aspen-db-data.bucket}/phylo_run/*"
              ]
          }
      ]
  }
  POLICY
}


resource "aws_iam_role_policy_attachment" "aspen-batch-job-can-submit-more-jobs" {
  role       = aws_iam_role.aspen-batch-jobs-role.name
  policy_arn = aws_iam_policy.can-submit-aspen-batch-job.arn
}


resource "aws_iam_role_policy_attachment" "aspen-batch-job-policies" {
  role       = aws_iam_role.aspen-batch-jobs-role.name
  policy_arn = aws_iam_policy.aspen-batch-jobs-policies.arn
}
