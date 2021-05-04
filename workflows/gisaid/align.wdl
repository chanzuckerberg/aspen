#!/bin/bash

set -Eeuo pipefail
shopt -s inherit_errexit

if [ $# -ne 1 ]; then
    echo "Usage: $0 <processed_gisaid_object_id>"
    exit 1
fi

# install jq
apt-get install -y jq

# get the bucket/key from the object id
processed_gisaid_location=$(/aspen/.venv/bin/python src/backend/aspen/workflows/align_gisaid/lookup_processed_gisaid_object.py --processed-gisaid-object-id "${1}")
processed_gisaid_s3_bucket=$(echo "${processed_gisaid_location}" | jq -r .bucket)
processed_gisaid_sequences_s3_key=$(echo "${processed_gisaid_location}" | jq -r .sequences_key)
processed_gisaid_metadata_s3_key=$(echo "${processed_gisaid_location}" | jq -r .metadata_key)

start_time=$(date +%s)
build_id=$(date +%Y%m%d-%H%M)

# set up ncov
mkdir -p /ncov/my_profiles/align
cd /ncov
git init
git fetch --depth 1 git://github.com/nextstrain/ncov.git
git checkout FETCH_HEAD
ncov_git_rev=$(git rev-parse HEAD)
cp /aspen/src/backend/aspen/workflows/align_gisaid/config.yaml /ncov/my_profiles/align

# fetch the gisaid dataset
aws s3 cp --no-progress s3://"${processed_gisaid_s3_bucket}"/"${processed_gisaid_sequences_s3_key}" - | xz -d > /ncov/data/sequences.fasta
aws s3 cp --no-progress s3://"${processed_gisaid_s3_bucket}"/"${processed_gisaid_metadata_s3_key}" /ncov/data/metadata.tsv
snakemake --printshellcmds results/aligned.fasta --profile my_profiles/align/

xz -2 /ncov/results/aligned.fasta

# upload the files to S3
bucket=aspen-db-data-"${DEPLOYMENT_ENVIRONMENT}"
sequences_key=aligned_gisaid_dump/"${build_id}"/sequences.fasta.xz
metadata_key=aligned_gisaid_dump/"${build_id}"/metadata.tsv
aws s3 cp /ncov/results/aligned.fasta.xz s3://"${bucket}"/"${sequences_key}"
aws s3 cp /ncov/data/metadata.tsv s3://"${bucket}"/"${metadata_key}"

cd /aspen/

# update aspen
aspen_workflow_rev=$(git rev-parse HEAD)
git fetch --depth 1 git://github.com/chanzuckerberg/aspen "$ASPEN_GIT_REVSPEC"
git checkout FETCH_HEAD
aspen_creation_rev=$(git rev-parse HEAD)

if [ "${aspen_workflow_rev}" != "${aspen_creation_rev}" ]; then
    # reinstall aspen
    /aspen/.venv/bin/pip install -e src/backend
fi

end_time=$(date +%s)

# create the objects
entity_id=$(/aspen/.venv/bin/python /aspen/src/backend/aspen/workflows/align_gisaid/save.py                 \
                                    --aspen-workflow-rev "${aspen_workflow_rev}"                            \
                                    --aspen-creation-rev "${aspen_creation_rev}"                            \
                                    --ncov-rev "${ncov_git_rev}"                                            \
                                    --aspen-docker-image-version "${ASPEN_DOCKER_IMAGE_VERSION}"            \
                                    --start-time "${start_time}"                                            \
                                    --end-time "${end_time}"                                                \
                                    --processed-gisaid-object-id "${1}"                                     \
                                    --gisaid-s3-bucket "${bucket}"                                          \
                                    --gisaid-sequences-s3-key "${sequences_key}"                            \
                                    --gisaid-metadata-s3-key "${metadata_key}"                              \
         )
