resource "aws_s3_bucket" "aspen-db-data" {
  bucket = join("", ["aspen-db-data-", var.DEPLOYMENT_ENVIRONMENT])
  acl = "private"
}


resource "aws_s3_bucket" "aspen-external-auspice-data" {
  bucket = join("", ["aspen-external-auspice-data-", var.DEPLOYMENT_ENVIRONMENT])
  acl = "private"

  lifecycle_rule {
    id      = "expire"
    enabled = true

    expiration {
      days = 30
    }
  }
}
