#!/bin/bash

set -Eeuxo pipefail

# install miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda
source ~/.bashrc

# install pangolin
mkdir pangolin
cd pangolin
git init
git fetch --depth 1 git@github.com:cov-lineages/pangolin.git
git checkout FETCH_HEAD
conda env create -f environment.yml
conda activate pangolin
python setup.py install

# check pangolin installation worked:
pangolin -pv

# process all trailing args to include --sample-public-identifiers flag
args=""
for sample_id in "${@}"
do
    args="$args --sample-public-identifier $sample_id"
done

sequences_output = "sequences.fasta"

# call export script to export renamed sequences
/aspen/.venv/bin/python /aspen/src/backend/workflows/pangolin/export.py \
  --public-identifiers $args \
  --sequences $sequences_output


# call pangolin on the exported sequences
lineage_report = "lineage_report.csv"
pangolin $sequences_output --outfile $lineage_report

last_updated = date +'%m-%d-%Y'
# save the pangolin results back to the db:
/aspen/.venv/bin/python /aspen/src/backend/workflows/pangolin/save.py \
  --pangolin-csv $lineage_report \
  --pangolin-last-updated $last_updated