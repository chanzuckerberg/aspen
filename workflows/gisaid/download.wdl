version 1.1

task RefreshGisaid {
    input {
        String docker_image_id = "aspen-gisaid"
        String aws_region = "us-west-2"
        String gisaid_ndjson_export_url = "https://www.epicov.org/epi3/3p/exp3/export/export.json.bz2"
        String gisaid_ndjson_staging_bucket = "akislyuk-aspen-experiments"
        String gisaid_ndjson_staging_key = "gisaid.ndjson.xz"
    }

    command <<<
    set -Eeuo pipefail
    shopt -s inherit_errexit

    start_time=$(date +%s)
    build_id=$(date +%Y%m%d-%H%M)

    # fetch the gisaid dataset and transform it.
    aws configure set region ~{aws_region}
    gisaid_credentials=$(aws secretsmanager get-secret-value --secret-id gisaid-download-credentials --query SecretString --output text)
    gisaid_username=$(echo "${gisaid_credentials}" | jq -r .username)
    gisaid_password=$(echo "${gisaid_credentials}" | jq -r .password)

    staged_timestamp=0
    if aws s3api head-object --bucket ~{gisaid_ndjson_staging_bucket} --key ~{gisaid_ndjson_staging_key}; then
        staged_timestamp=$(aws s3api head-object --bucket ~{gisaid_ndjson_staging_bucket} --key ~{gisaid_ndjson_staging_key} | jq -r .LastModified)
    fi
    if curl --silent --head --time-cond "$staged_timestamp" "~{gisaid_ndjson_export_url}" --user "${gisaid_username}":"${gisaid_password}" | head -n 1 | grep 304; then
        echo "File at ~{gisaid_ndjson_export_url} has not been modified since $staged_timestamp, nothing to do"
        exit
    fi
    curl "~{gisaid_ndjson_export_url}" --user "${gisaid_username}":"${gisaid_password}" | \
        bunzip2 | \
        xz -2 -c | \
        aws s3 cp - s3://~{gisaid_ndjson_staging_bucket}/~{gisaid_ndjson_staging_key}
    >>>

    output {
    }

    runtime {
        docker: docker_image_id
    }
}
