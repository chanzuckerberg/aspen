resource "aws_s3_bucket_object" "wdl" {
  bucket = var.swipe_wdl_bucket
  key    = "${var.remote_dev_prefix}/${basename(var.wdl_path)}-v0.0.1.wdl" # Swipe lambdas require specially formatted filenames.
  source = "${path.module}/gisaid.wdl" # TODO this is a haaaack!

  etag = filemd5("${path.module}/gisaid.wdl")
}

resource "aws_ssm_parameter" "run_config" {
  name = "${var.stack_resource_prefix}-${var.deployment_stage}-${var.custom_stack_name}-${var.app_name}"
  type  = "String"
  value = jsonencode({
    Input = {
      Run = {
        docker_image_id = var.image
      }
    }
    OutputPrefix = "s3://${var.swipe_comms_bucket}/swipe${var.remote_dev_prefix}/${var.app_name}/results",
    RunSPOTMemory = var.memory
    RunEC2Memory = var.memory
    RUN_WDL_URI = "s3://${aws_s3_bucket_object.wdl.bucket}${aws_s3_bucket_object.wdl.key}"
  })
}
