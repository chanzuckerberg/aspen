#!/bin/bash

set -Eeuo pipefail
shopt -s inherit_errexit

# install jq
apt-get install -y jq

start_time=$(date +%s)
build_id=$(date +%Y%m%d-%H%M)

# fetch the gisaid dataset and transform it.
gisaid_credentials=$(aws secretsmanager get-secret-value --secret-id gisaid-download-credentials --query SecretString --output text)
gisaid_username=$(echo "${gisaid_credentials}" | jq -r .username)
gisaid_password=$(echo "${gisaid_credentials}" | jq -r .password)

curl "https://www.epicov.org/epi3/3p/exp3/export/export.json.bz2" --user "${gisaid_username}":"${gisaid_password}" | bunzip2 | xz -2 -c > /aspen/gisaid.ndjson.xz

bucket=aspen-db-data-"${DEPLOYMENT_ENVIRONMENT}"
key=raw_gisaid_dump/"${build_id}"/gisaid.ndjson.xz
aws s3 cp /aspen/gisaid.ndjson.xz s3://"${bucket}"/"${key}"

cd /aspen/

# update aspen
aspen_workflow_rev=$(git rev-parse HEAD)
git fetch --depth 1 git://github.com/chanzuckerberg/aspen "${ASPEN_GIT_REVSPEC}"
git checkout FETCH_HEAD
aspen_creation_rev=$(git rev-parse HEAD)

if [ "${aspen_workflow_rev}" != "${aspen_creation_rev}" ]; then
    # reinstall aspen
    /aspen/.venv/bin/pip install -e src/backend
fi

end_time=$(date +%s)

# create the objects
entity_id=$(/aspen/.venv/bin/python /aspen/src/backend/aspen/workflows/ingest_gisaid/save.py \
                                    --aspen-workflow-rev "${aspen_workflow_rev}"             \
                                    --aspen-creation-rev "${aspen_creation_rev}"             \
                                    --start-time "${start_time}"                             \
                                    --end-time "${end_time}"                                 \
                                    --gisaid-s3-bucket "${bucket}"                           \
                                    --gisaid-s3-key "${key}"                                 \
         )

# invoke the next workflow
aws batch submit-job \
    --job-name "transform-gisaid"                \
    --job-queue aspen-batch                      \
    --job-definition aspen-batch-job-definition  \
    --container-overrides "
      {
        \"command\": [\"${ASPEN_GIT_REVSPEC}\", \"src/backend/aspen/workflows/transform_gisaid/transform.sh\", \"${entity_id}\"],
        \"memory\": 15000
      }"
