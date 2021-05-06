# This deploys an Aspen stack.
#

data aws_secretsmanager_secret_version config {
  secret_id = var.happy_config_secret
}

locals {
  secret = jsondecode(data.aws_secretsmanager_secret_version.config.secret_string)
  alb_key = var.require_okta ? "private_albs" : "public_albs"

  custom_stack_name     = var.stack_name
  image_tag             = var.image_tag
  priority              = var.priority
  deployment_stage      = var.deployment_stage
  remote_dev_prefix     = var.stack_prefix
  wait_for_steady_state = var.wait_for_steady_state

  migration_cmd         = ["make", "remote-db-migrations"]
  deletion_cmd          = ["make", "remote-db-drop"]
  backend_cmd           = []
  frontend_cmd          = ["npm", "run", "serve"]
  data_load_path        = length(var.sql_import_file) > 0 ? "${local.secret["s3_buckets"]["aspen"]["name"]}/${var.sql_import_file}" : ""

  vpc_id                = local.secret["vpc_id"]
  subnets               = local.secret["private_subnets"]
  security_groups       = local.secret["security_groups"]
  zone                  = local.secret["zone_id"]
  cluster               = local.secret["cluster_arn"]

  swipe_comms_bucket    = local.secret["s3_buckets"]["aspen_swipe_comms"]["name"]
  swipe_wdl_bucket      = local.secret["s3_buckets"]["aspen_swipe_wdl"]["name"]
  aspen_data_bucket     = local.secret["s3_buckets"]["aspen"]["name"]

  # Web images
  frontend_image_repo   = local.secret["ecrs"]["frontend"]["url"]
  backend_image_repo    = local.secret["ecrs"]["backend"]["url"]

  # Workflow images
  pangolin_image_repo   = local.secret["ecrs"]["pangolin"]["url"]
  phylotree_image_repo  = local.secret["ecrs"]["phylotree"]["url"]
  gisaid_image_repo     = local.secret["ecrs"]["gisaid"]["url"]

  # This is the wdl executor image, doesn't change on update.
  swipe_image_repo     = local.secret["ecrs"]["swipe"]["url"]

  batch_role_arn        = local.secret["batch_queues"]["aspen"]["role_arn"]
  ec2_queue_arn         = local.secret["batch_envs"]["aspen"]["envs"]["EC2"]["queue_arn"]
  spot_queue_arn        = local.secret["batch_envs"]["aspen"]["envs"]["SPOT"]["queue_arn"]
  external_dns          = local.secret["external_zone_name"]
  internal_dns          = local.secret["internal_zone_name"]

  frontend_listener_arn = local.secret[local.alb_key]["frontend"]["listener_arn"]
  backend_listener_arn  = local.secret[local.alb_key]["backend"]["listener_arn"]
  frontend_alb_zone     = local.secret[local.alb_key]["frontend"]["zone_id"]
  backend_alb_zone      = local.secret[local.alb_key]["backend"]["zone_id"]
  frontend_alb_dns      = local.secret[local.alb_key]["frontend"]["dns_name"]
  backend_alb_dns       = local.secret[local.alb_key]["backend"]["dns_name"]

  ecs_role_arn          = local.secret["service_roles"]["ecs_role"]
  sfn_role_arn          = local.secret["service_roles"]["sfn_nextstrain"]

  frontend_url = try(join("", ["https://", module.frontend_dns[0].dns_prefix, ".", local.external_dns]), var.frontend_url)
  backend_url  = try(join("", ["https://", module.backend_dns[0].dns_prefix, ".", local.external_dns]), var.backend_url)

  stack_resource_prefix = "aspen"
}

module frontend_dns {
  count                 = var.require_okta ? 1 : 0
  stack_resource_prefix = local.stack_resource_prefix
  source                = "../dns"
  custom_stack_name     = local.custom_stack_name
  app_name              = "frontend"
  alb_dns               = local.frontend_alb_dns
  canonical_hosted_zone = local.frontend_alb_zone
  zone                  = local.internal_dns
}

module backend_dns {
  count                 = var.require_okta ? 1 : 0
  stack_resource_prefix = local.stack_resource_prefix
  source                = "../dns"
  custom_stack_name     = local.custom_stack_name
  app_name              = "backend"
  alb_dns               = local.backend_alb_dns
  canonical_hosted_zone = local.backend_alb_zone
  zone                  = local.internal_dns
}

module frontend_service {
  source                = "../service"
  stack_resource_prefix = local.stack_resource_prefix
  custom_stack_name     = local.custom_stack_name
  app_name              = "frontend"
  vpc                   = local.vpc_id
  image                 = "${local.frontend_image_repo}:${local.image_tag}"
  cluster               = local.cluster
  desired_count         = 2
  listener              = local.frontend_listener_arn
  subnets               = local.subnets
  security_groups       = local.security_groups
  task_role_arn         = local.ecs_role_arn
  service_port          = 3000
  cmd                   = local.frontend_cmd
  deployment_stage      = local.deployment_stage
  step_function_arn     = module.swipe_sfn.step_function_arn
  host_match            = try(join(".", [module.frontend_dns[0].dns_prefix, local.external_dns]), "")
  priority              = local.priority
  api_url               = local.backend_url
  frontend_url          = local.frontend_url
  remote_dev_prefix     = local.remote_dev_prefix

  wait_for_steady_state = local.wait_for_steady_state
}

module backend_service {
  source                = "../service"
  stack_resource_prefix = local.stack_resource_prefix
  custom_stack_name     = local.custom_stack_name
  app_name              = "backend"
  vpc                   = local.vpc_id
  image                 = "${local.backend_image_repo}:${local.image_tag}"
  cluster               = local.cluster
  desired_count         = 2
  listener              = local.backend_listener_arn
  subnets               = local.subnets
  security_groups       = local.security_groups
  task_role_arn         = local.ecs_role_arn
  service_port          = 3000
  cmd                   = local.backend_cmd
  deployment_stage      = local.deployment_stage
  step_function_arn     = module.swipe_sfn.step_function_arn
  host_match            = try(join(".", [module.backend_dns[0].dns_prefix, local.external_dns]), "")
  priority              = local.priority
  api_url               = local.backend_url
  frontend_url          = local.frontend_url
  remote_dev_prefix     = local.remote_dev_prefix
  health_check_path     = "/health"

  wait_for_steady_state = local.wait_for_steady_state
}

module swipe_sfn {
  source                 = "../swipe-sfn"
  app_name               = "swipe-sfn"
  stack_resource_prefix  = local.stack_resource_prefix
  remote_dev_prefix      = local.remote_dev_prefix
  job_definition_name    = module.swipe_batch.batch_job_definition
  ec2_queue_arn          = local.ec2_queue_arn
  spot_queue_arn         = local.spot_queue_arn
  role_arn               = local.sfn_role_arn
  custom_stack_name      = local.custom_stack_name
  deployment_stage       = local.deployment_stage
}

# Write information on how to invoke the gisaid sfn to SSM.
module gisaid_sfn_config {
  source   = "../sfn_config"
  app_name = "gisaid-sfn"
  image    = "${local.gisaid_image_repo}:${local.image_tag}"
  memory   = 420000
  wdl_path = "workflows/gisaid.wdl"
  custom_stack_name     = local.custom_stack_name
  deployment_stage      = local.deployment_stage
  remote_dev_prefix     = local.remote_dev_prefix
  stack_resource_prefix = local.stack_resource_prefix
  swipe_comms_bucket    = local.swipe_comms_bucket
  swipe_wdl_bucket      = local.swipe_wdl_bucket
  data_bucket           = local.aspen_data_bucket
}

module migrate_db {
  source                = "../migration"
  stack_resource_prefix = local.stack_resource_prefix
  image                 = "${local.backend_image_repo}:${local.image_tag}"
  task_role_arn         = local.ecs_role_arn
  cmd                   = local.migration_cmd
  custom_stack_name     = local.custom_stack_name
  remote_dev_prefix     = local.remote_dev_prefix
  deployment_stage      = local.deployment_stage
  data_load_path        = local.data_load_path
}

module delete_db {
  count                 = var.delete_protected ? 0 : 1
  stack_resource_prefix = local.stack_resource_prefix
  source                = "../deletion"
  image                 = "${local.backend_image_repo}:${local.image_tag}"
  task_role_arn         = local.ecs_role_arn
  cmd                   = local.deletion_cmd
  custom_stack_name     = local.custom_stack_name
  remote_dev_prefix     = local.remote_dev_prefix
  deployment_stage      = local.deployment_stage
}

module swipe_batch {
  source                = "../batch"
  app_name              = "swipe"
  stack_resource_prefix = local.stack_resource_prefix
  image                 = "${local.swipe_image_repo}:latest" # TODO hardcoded
  batch_role_arn        = local.batch_role_arn
  custom_stack_name     = local.custom_stack_name
  remote_dev_prefix     = local.remote_dev_prefix
  deployment_stage      = local.deployment_stage
  frontend_url          = local.frontend_url
}
