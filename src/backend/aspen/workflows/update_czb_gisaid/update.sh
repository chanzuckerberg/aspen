#!/bin/bash

set -Eeuxo pipefail
shopt -s inherit_errexit

# install jq
apt-get install -y jq

czb_credentials=$(aws secretsmanager get-secret-value --secret-id czb-aws-access --query SecretString --output text)
aws_access_key_id=$(echo "$czb_credentials" | jq -r .AWS_ACCESS_KEY_ID)
aws_secret_access_key=$(echo "$czb_credentials" | jq -r .AWS_SECRET_ACCESS_KEY)

# get the bucket/key from the object id
processed_gisaid_location=$(/aspen/.venv/bin/python src/backend/aspen/workflows/update_czb_gisaid/lookup_latest_processed_gisaid.py)
processed_gisaid_s3_bucket=$(echo "${processed_gisaid_location}" | jq -r .bucket)
processed_gisaid_sequences_s3_key=$(echo "${processed_gisaid_location}" | jq -r .sequences_key)
processed_gisaid_metadata_s3_key=$(echo "${processed_gisaid_location}" | jq -r .metadata_key)

start_time=$(date +%s)
build_id=$(date +%Y%m%d-%H%M)

# fetch the gisaid dataset
aws s3 cp --no-progress s3://"${processed_gisaid_s3_bucket}"/"${processed_gisaid_sequences_s3_key}" - | xz -d | gzip -c > /sequences.fasta.gz
aws s3 cp --no-progress s3://"${processed_gisaid_s3_bucket}"/"${processed_gisaid_metadata_s3_key}" - | gzip -c > /metadata.tsv.gz

# upload the files to S3
bucket=czb-covid-results
sequences_key=gisaid/sequences.fasta.gz
metadata_key=gisaid/metadata.tsv.gz
AWS_ACCESS_KEY_ID="$aws_access_key_id" AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" aws s3 cp /sequences.fasta.gz s3://"${bucket}"/"${sequences_key}"
AWS_ACCESS_KEY_ID="$aws_access_key_id" AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" aws s3 cp /metadata.tsv.gz s3://"${bucket}"/"${metadata_key}"
