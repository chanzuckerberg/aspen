version 1.1

workflow LoadGISAID {
    input {
        String docker_image_id = "aspen-gisaid"
        String aws_region = "us-west-2"
        String db_data_bucket = "aspen-db-data-dev"
        String gisaid_ndjson_export_url = "https://www.epicov.org/epi3/3p/exp3/export/export.json.bz2"
        String gisaid_ndjson_staging_bucket = "aspen-data-dev"
        String gisaid_ndjson_staging_key = "raw_gisaid_dump/test.zst"
    }

    call RefreshGISAID {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        gisaid_ndjson_export_url = gisaid_ndjson_export_url,
        gisaid_ndjson_staging_bucket = gisaid_ndjson_staging_bucket,
        gisaid_ndjson_staging_key = gisaid_ndjson_staging_key
    }

    call IngestGISAID {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        gisaid_ndjson_staging_bucket = gisaid_ndjson_staging_bucket,
        gisaid_ndjson_staging_key = gisaid_ndjson_staging_key
    }

    call TransformGISAID {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        raw_gisaid_object_id = IngestGISAID.entity_id,
        raw_gisaid_object = "s3://~{gisaid_ndjson_staging_bucket}/~{gisaid_ndjson_staging_key}",
        db_data_bucket = db_data_bucket
    }

    call AlignGISAID {
        input:
        docker_image_id = docker_image_id,
        aws_region = aws_region,
        processed_gisaid_object_id = TransformGISAID.entity_id,
        db_data_bucket = db_data_bucket
    }

    output {
        Array[File] snakemake_logs = AlignGISAID.snakemake_logs
        File align_log = AlignGISAID.align_log
        String ingest_entity_id = IngestGISAID.entity_id
        String transform_entity_id = TransformGISAID.entity_id
        String align_entity_id = AlignGISAID.entity_id
    }
}

task RefreshGISAID {
    input {
        String docker_image_id
        String aws_region
        String gisaid_ndjson_export_url
        String gisaid_ndjson_staging_bucket
        String gisaid_ndjson_staging_key
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
        zstdmt | \
        aws s3 cp - s3://~{gisaid_ndjson_staging_bucket}/~{gisaid_ndjson_staging_key}
    >>>

    output {
    }

    runtime {
        docker: docker_image_id
    }
}

task IngestGISAID {
    input {
        String docker_image_id = "aspen-gisaid"
        String aws_region = "us-west-2"
        String gisaid_ndjson_staging_bucket = "akislyuk-aspen-experiments"
        String gisaid_ndjson_staging_key = "gisaid.3.ndjson.xz"
    }

    command <<<
    set -Eeuo pipefail
    set -x
    shopt -s inherit_errexit

    start_time=$(date +%s)
    build_id=$(date +%Y%m%d-%H%M)
    end_time=$(date +%s)
    aspen_workflow_rev=$(git -C /aspen rev-parse HEAD)
    aspen_creation_rev=$(git -C /aspen rev-parse HEAD)

    aws configure set region ~{aws_region}

    # create the objects
    python3 /aspen/src/backend/aspen/workflows/ingest_gisaid/save.py \
            --aspen-workflow-rev "${aspen_workflow_rev}"             \
            --aspen-creation-rev "${aspen_creation_rev}"             \
            --start-time "${start_time}"                             \
            --end-time "${end_time}"                                 \
            --gisaid-s3-bucket "~{gisaid_ndjson_staging_bucket}"     \
            --gisaid-s3-key "~{gisaid_ndjson_staging_key}" > entity_id
    >>>

    output {
        String entity_id = read_string("entity_id")
    }

    runtime {
        docker: docker_image_id
    }
}

task TransformGISAID {
    input {
        String docker_image_id = "aspen-gisaid"
        String aws_region = "us-west-2"
        String raw_gisaid_object_id
        File raw_gisaid_object
        String db_data_bucket = "aspen-db-data-dev"
    }

    command <<<
    set -Eeuo pipefail
    set -x
    shopt -s inherit_errexit

    aws configure set region ~{aws_region}

    start_time=$(date +%s)
    build_id=$(date +%Y%m%d-%H%M)
    aspen_creation_rev=$(git -C /aspen rev-parse HEAD)
    aspen_workflow_rev=$(git -C /aspen rev-parse HEAD)
    
    ncov_ingest_git_rev=$(git -C /ncov-ingest rev-parse HEAD)

    # decompress the gisaid dataset and transform it.
    zstdmt -d --stdout ~{raw_gisaid_object} > gisaid.ndjson
    /ncov-ingest/bin/transform-gisaid \
        gisaid.ndjson                     \
        --output-metadata metadata.tsv    \
        --output-fasta sequences.fasta    \
        --output-unix-newline

    zstdmt sequences.fasta
    ls -lR

    # upload the files to S3
    bucket=~{db_data_bucket}
    sequences_key=processed_gisaid_dump/"${build_id}"/sequences.fasta.zst
    metadata_key=processed_gisaid_dump/"${build_id}"/metadata.tsv
    aws s3 cp sequences.fasta.zst s3://"${bucket}"/"${sequences_key}"
    aws s3 cp metadata.tsv s3://"${bucket}"/"${metadata_key}"
    end_time=$(date +%s)

    # create the objects
    python3 /aspen/src/backend/aspen/workflows/transform_gisaid/save.py \
            --aspen-workflow-rev "${aspen_workflow_rev}"            \
            --aspen-creation-rev "${aspen_creation_rev}"            \
            --ncov-ingest-rev "${ncov_ingest_git_rev}"              \
            --start-time "${start_time}"                            \
            --end-time "${end_time}"                                \
            --raw-gisaid-object-id "~{raw_gisaid_object_id}"        \
            --gisaid-s3-bucket "${bucket}"                          \
            --gisaid-sequences-s3-key "${sequences_key}"            \
            --gisaid-metadata-s3-key "${metadata_key}" > entity_id
    >>>

    output {
        String entity_id = read_string("entity_id")
    }

    runtime {
        docker: docker_image_id
    }
}

task AlignGISAID {
    input {
        String docker_image_id
        String aws_region = "u-west-2"
        String processed_gisaid_object_id
        String db_data_bucket = "aspen-db-data-dev"
    }

    command <<<
    set -Eeuo pipefail
    shopt -s inherit_errexit

    aws configure set region ~{aws_region}

    # get the bucket/key from the object id
    processed_gisaid_location=$(python3 /aspen/src/backend/aspen/workflows/align_gisaid/lookup_processed_gisaid_object.py --processed-gisaid-object-id "~{processed_gisaid_object_id}")
    processed_gisaid_s3_bucket=$(echo "${processed_gisaid_location}" | jq -r .bucket)
    processed_gisaid_sequences_s3_key=$(echo "${processed_gisaid_location}" | jq -r .sequences_key)
    processed_gisaid_metadata_s3_key=$(echo "${processed_gisaid_location}" | jq -r .metadata_key)

    start_time=$(date +%s)
    build_id=$(date +%Y%m%d-%H%M)

    ncov_git_rev=$(git -C /ncov rev-parse HEAD)

    # fetch the gisaid dataset
    aws s3 cp --no-progress s3://"${processed_gisaid_s3_bucket}"/"${processed_gisaid_sequences_s3_key}" - | zstdmt -d > /ncov/data/sequences.fasta
    aws s3 cp --no-progress s3://"${processed_gisaid_s3_bucket}"/"${processed_gisaid_metadata_s3_key}" /ncov/data/metadata.tsv
    (cd /ncov; snakemake --printshellcmds results/aligned.fasta --profile /aspen/src/backend/aspen/workflows/align_gisaid 1>&2)

    mv /ncov/.snakemake/log/*.snakemake.log /ncov/logs/align.txt .

    zstdmt /ncov/results/aligned.fasta

    # upload the files to S3
    bucket="~{db_data_bucket}"
    sequences_key=aligned_gisaid_dump/"${build_id}"/sequences.fasta.zst
    metadata_key=aligned_gisaid_dump/"${build_id}"/metadata.tsv
    aws s3 cp /ncov/results/aligned.fasta.zst s3://"${bucket}"/"${sequences_key}"
    aws s3 cp /ncov/data/metadata.tsv s3://"${bucket}"/"${metadata_key}"

    aspen_creation_rev=$(git -C /aspen rev-parse HEAD)
    aspen_workflow_rev=$(git -C /aspen rev-parse HEAD)

    end_time=$(date +%s)

    # create the objects
    python3 /aspen/src/backend/aspen/workflows/align_gisaid/save.py                 \
            --aspen-workflow-rev "${aspen_workflow_rev}"                            \
            --aspen-creation-rev "${aspen_creation_rev}"                            \
            --ncov-rev "${ncov_git_rev}"                                            \
            --aspen-docker-image-version "externally_managed"                       \
            --start-time "${start_time}"                                            \
            --end-time "${end_time}"                                                \
            --processed-gisaid-object-id "~{processed_gisaid_object_id}"            \
            --gisaid-s3-bucket "${bucket}"                                          \
            --gisaid-sequences-s3-key "${sequences_key}"                            \
            --gisaid-metadata-s3-key "${metadata_key}" > entity_id
    >>>

    output {
        Array[File] snakemake_logs = glob("*.snakemake.log")
        File align_log = "align.txt"
        String entity_id = read_string("entity_id")
    }

    runtime {
        docker: docker_image_id
    }
}
