variable "aspen-batch-params" {
  type  = map
  default = {
    timeout = 14400
  }
}

data "aws_region" "current" {}


resource "aws_batch_job_definition" "aspen-batch-job-definition" {
  name = "aspen-batch-job-definition"
  type = "container"
  parameters = var.aspen-batch-params

  container_properties = <<CONTAINER_PROPERTIES
{
    "command": [],
    "image": "cziaspen/batch:latest",
    "memory": 1024,
    "vcpus": 1,
    "jobRoleArn": "${aws_iam_role.aspen-batch-jobs-role.arn}",
    "environment": [
      {"name": "AWS_DEFAULT_REGION", "value": "${data.aws_region.current.name}"},
      {"name": "DEPLOYMENT_ENVIRONMENT", "value": "${var.DEPLOYMENT_ENVIRONMENT}"}
    ]
}
CONTAINER_PROPERTIES
}


resource "aws_security_group" "aspen-batch-security-group" {
  name = "aspen_aws_batch_compute_environment_security_group"
  description = "security group for aspen batch"
  vpc_id = aws_default_vpc.default.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


data "aws_ssm_parameter" "amazon-linux-2-ecs-image" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended/image_id"
}


# for increased disk space
resource "aws_launch_template" "aspen-batch-launch-template" {
  name = "aspen-batch-launch-template"

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size = 200
      volume_type = "gp2"
      delete_on_termination = true
    }
  }
  image_id = data.aws_ssm_parameter.amazon-linux-2-ecs-image.value
  update_default_version = true
}


resource "aws_batch_compute_environment" "aspen-batch-compute-environment" {
  compute_environment_name_prefix = "aspen-batch-"

  compute_resources {
    instance_role = aws_iam_instance_profile.batch-ecs-instance-role.arn
    allocation_strategy = "BEST_FIT"
    # TODO: create common ec2 key
    ec2_key_pair = "ttung"

    instance_type = [
      "r5",
    ]

    max_vcpus = 128
    min_vcpus = 1

    security_group_ids = [
      aws_security_group.aspen-batch-security-group.id,
    ]

    subnets = aws_default_subnet.default.*.id

    type = "EC2"

    launch_template {
      launch_template_id = aws_launch_template.aspen-batch-launch-template.id
      version = aws_launch_template.aspen-batch-launch-template.latest_version
    }
  }

  service_role = aws_iam_role.batch-service-role.arn
  type = "MANAGED"
  depends_on   = [
    aws_iam_role_policy_attachment.batch-service-role
  ]

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_batch_job_queue" "aspen-batch-job-queue" {
  name     = "aspen-batch"
  state    = "ENABLED"
  priority = 1
  compute_environments = [
    aws_batch_compute_environment.aspen-batch-compute-environment.arn,
  ]
}
