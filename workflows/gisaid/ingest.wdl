version 1.1

task IngestGisaid {
    input {
        String docker_image_id = "aspen-gisaid"
        String aws_region = "us-west-2"
        String gisaid_ndjson_staging_bucket = "akislyuk-idseq-experiments"
        String gisaid_ndjson_staging_key = "gisaid.ndjson.xz"
    }

    command <<<
    set -Eeuo pipefail
    shopt -s inherit_errexit

    start_time=$(date +%s)
    build_id=$(date +%Y%m%d-%H%M)
    end_time=$(date +%s)
    aspen_workflow_rev=$(git -C /aspen rev-parse HEAD)
    aspen_creation_rev=$(git -C /aspen rev-parse HEAD)

    aws configure set region ~{aws_region}

    # create the objects
    /aspen/.venv/bin/python3 /aspen/src/backend/aspen/workflows/ingest_gisaid/save.py \
                             --aspen-workflow-rev "${aspen_workflow_rev}"             \
                             --aspen-creation-rev "${aspen_creation_rev}"             \
                             --start-time "${start_time}"                             \
                             --end-time "${end_time}"                                 \
                             --gisaid-s3-bucket "~{gisaid_ndjson_staging_bucket}"     \
                             --gisaid-s3-key "~{gisaid_ndjson_staging_key}" > /entity_id
    >>>

    output {
        String entity_id = read_string("/entity_id")
    }

    runtime {
        docker: docker_image_id
    }
}

