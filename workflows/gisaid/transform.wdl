#!/bin/bash

set -Eeuo pipefail
shopt -s inherit_errexit

if [ $# -ne 1 ]; then
    echo "Usage: $0 <raw_gisaid_object_id>"
    exit 1
fi

# install jq and gcc (gcc is for netifaces, a python package)
apt-get install -y jq gcc

# get the bucket/key from the object id
raw_gisaid_location=$(/aspen/.venv/bin/python src/backend/aspen/workflows/transform_gisaid/lookup_raw_gisaid_object.py --raw-gisaid-object-id "${1}")
raw_gisaid_s3_bucket=$(echo "${raw_gisaid_location}" | jq -r .bucket)
raw_gisaid_s3_key=$(echo "${raw_gisaid_location}" | jq -r .key)

start_time=$(date +%s)
build_id=$(date +%Y%m%d-%H%M)

# set up ncov-ingest's environment
mkdir -p /ncov-ingest/data/gisaid
cd /ncov-ingest
git init
git fetch --depth 1 git://github.com/nextstrain/ncov-ingest.git
git checkout FETCH_HEAD
ncov_ingest_git_rev=$(git rev-parse HEAD)
python3.7 -m venv /ncov-ingest/.venv
source /ncov-ingest/.venv/bin/activate
pip install -U pip pipenv
pipenv install

# fetch the gisaid dataset and transform it.
aws s3 cp --no-progress s3://"${raw_gisaid_s3_bucket}"/"${raw_gisaid_s3_key}" - | xz -d > data/gisaid.ndjson
./bin/transform-gisaid /ncov-ingest/data/gisaid.ndjson                            \
                       --output-metadata /ncov-ingest/data/gisaid/metadata.tsv    \
                       --output-fasta /ncov-ingest/data/gisaid/sequences.fasta    \
                       --output-unix-newline

xz -2 /ncov-ingest/data/gisaid/sequences.fasta
ls -lR data

# upload the files to S3
bucket=aspen-db-data-"${DEPLOYMENT_ENVIRONMENT}"
sequences_key=processed_gisaid_dump/"${build_id}"/sequences.fasta.xz
metadata_key=processed_gisaid_dump/"${build_id}"/metadata.tsv
aws s3 cp /ncov-ingest/data/gisaid/sequences.fasta.xz s3://"${bucket}"/"${sequences_key}"
aws s3 cp /ncov-ingest/data/gisaid/metadata.tsv s3://"${bucket}"/"${metadata_key}"

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
entity_id=$(/aspen/.venv/bin/python src/backend/aspen/workflows/transform_gisaid/save.py    \
                                    --aspen-workflow-rev "${aspen_workflow_rev}"            \
                                    --aspen-creation-rev "${aspen_creation_rev}"            \
                                    --ncov-ingest-rev "${ncov_ingest_git_rev}"              \
                                    --start-time "${start_time}"                            \
                                    --end-time "${end_time}"                                \
                                    --raw-gisaid-object-id "${1}"                           \
                                    --gisaid-s3-bucket "${bucket}"                          \
                                    --gisaid-sequences-s3-key "${sequences_key}"            \
                                    --gisaid-metadata-s3-key "${metadata_key}"              \
         )

# invoke the next workflow.
# NOTE: when the number of cpus is modified, it would be prudent to modify workflows/align_gisaid/config.yaml.
aws batch submit-job                             \
    --job-name "align-gisaid"                    \
    --job-queue aspen-batch                      \
    --job-definition aspen-batch-job-definition  \
    --container-overrides "
      {
        \"command\": [\"${ASPEN_GIT_REVSPEC}\", \"src/backend/aspen/workflows/align_gisaid/align.sh\", \"${entity_id}\"],
        \"vcpus\": 32,
        \"memory\": 420000
      }"
