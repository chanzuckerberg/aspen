#!/bin/bash
export AWS_REGION=us-west-2
export AWS_DEFAULT_REGION=us-west-2
export AWS_ACCESS_KEY_ID=nonce
export AWS_SECRET_ACCESS_KEY=nonce

export FRONTEND_URL=http://localhost:8000
export BACKEND_URL=http://localhost:3000

# NOTE: This script is intended to run INSIDE the dockerized dev environment!
# If you need to run it directly on your laptop for some reason, change
# localstack below to localhost
export LOCALSTACK_URL=http://localstack:4566

# How the backend can reach the OIDC idp
export OIDC_INTERNAL_URL=http://oidc
# How a web browser can reach the OIDC idp
export OIDC_BROWSER_URL=https://localhost:8443

echo "Creating secretsmanager secrets"
local_aws="aws --endpoint-url=${LOCALSTACK_URL}"
${local_aws} secretsmanager create-secret --name aspen-config &> /dev/null || true
${local_aws} secretsmanager update-secret --secret-id aspen-config --secret-string '{
  "AUTH0_CLIENT_ID": "local-client-id",
  "AUTH0_CALLBACK_URL": "'"${BACKEND_URL}"'/callback",
  "AUTH0_CLIENT_SECRET": "local-client-secret",
  "AUTH0_DOMAIN": "oidc",
  "AUTH0_BASE_URL": "'"${OIDC_INTERNAL_URL}"'",
  "AUTH0_USERINFO_URL": "connect/userinfo",
  "AUTH0_ACCESS_TOKEN_URL": "'"${OIDC_INTERNAL_URL}"'/connect/token",
  "AUTH0_AUTHORIZE_URL": "'"${OIDC_BROWSER_URL}"'/connect/authorize",
  "AUTH0_CLIENT_KWARGS": {"scope": "openid profile email offline_access"},
  "FLASK_SECRET": "DevelopmentKey",
  "DB/rw_username": "user_rw",
  "DB/rw_password": "password_rw",
  "DB/address": "database",
  "S3/external_auspice_bucket": "aspen-external-auspice-data"
}' || true

echo "Creating s3 buckets"
${local_aws} s3api head-bucket --bucket aspen-external-auspice-data || ${local_aws} s3 mb s3://aspen-external-auspice-data
