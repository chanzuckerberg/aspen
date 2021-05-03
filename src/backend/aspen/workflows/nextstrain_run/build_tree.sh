#!/bin/bash

set -Eeuxo pipefail
shopt -s inherit_errexit

if [ $# -ne 1 ]; then
    echo "Usage: $0 <phylo_run_id>"
    exit 1
fi

# install jq
apt-get install -y jq

build_id=$(date +%Y%m%d-%H%M)

# set up ncov
mkdir -p /ncov/my_profiles/aspen /ncov/results
cd /ncov
git init
git fetch --depth 1 git://github.com/nextstrain/ncov.git
git checkout FETCH_HEAD
ncov_git_rev=$(git rev-parse HEAD)

# patch ncov/scripts/combine-and-dedup-fastas.py
patch -p1 < /aspen/src/backend/aspen/workflows/nextstrain_run/combine-and-dedup-fastas.py.patch

cp /aspen/src/backend/aspen/workflows/nextstrain_run/nextstrain_profile/* /ncov/my_profiles/aspen/

# dump the sequences, metadata, and builds.yaml for a run out to disk.
aligned_gisaid_location=$(
    /aspen/.venv/bin/python /aspen/src/backend/aspen/workflows/nextstrain_run/export.py  \
                            --phylo-run-id "$1"                               \
                            --sequences /ncov/data/sequences_aspen.fasta      \
                            --metadata /ncov/data/metadata_aspen.tsv          \
                            --builds-file /ncov/my_profiles/aspen/builds.yaml \
)
aligned_gisaid_s3_bucket=$(echo "${aligned_gisaid_location}" | jq -r .bucket)
aligned_gisaid_sequences_s3_key=$(echo "${aligned_gisaid_location}" | jq -r .sequences_key)
aligned_gisaid_metadata_s3_key=$(echo "${aligned_gisaid_location}" | jq -r .metadata_key)

# fetch the gisaid dataset
aws s3 cp --no-progress s3://"${aligned_gisaid_s3_bucket}"/"${aligned_gisaid_sequences_s3_key}" - | xz -d > /ncov/results/aligned_gisaid.fasta
aws s3 cp --no-progress s3://"${aligned_gisaid_s3_bucket}"/"${aligned_gisaid_metadata_s3_key}" /ncov/data/metadata_gisaid.tsv

snakemake --printshellcmds auspice/ncov_aspen.json --profile my_profiles/aspen/  --resources=mem_mb=312320

# upload the tree to S3
bucket=aspen-db-data-"${DEPLOYMENT_ENVIRONMENT}"
key=phylo_run/"${build_id}"/ncov_aspen.json
aws s3 cp /ncov/auspice/ncov_aspen.json s3://"${bucket}"/"${key}"

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
/aspen/.venv/bin/python /aspen/src/backend/aspen/workflows/nextstrain_run/save.py               \
                        --aspen-workflow-rev "${aspen_workflow_rev}"                            \
                        --aspen-creation-rev "${aspen_creation_rev}"                            \
                        --ncov-rev "${ncov_git_rev}"                                            \
                        --aspen-docker-image-version "${ASPEN_DOCKER_IMAGE_VERSION}"            \
                        --end-time "${end_time}"                                                \
                        --phylo-run-id "$1"                                                     \
                        --bucket "$bucket"                                                      \
                        --key "$key"                                                            \
                        --tree-path /ncov/auspice/ncov_aspen.json                               \
