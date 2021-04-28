#!/bin/bash

set -Eeuxo pipefail

## install miniconda
#wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
#chmod +x Miniconda3-latest-Linux-x86_64.sh
#./Miniconda3-latest-Linux-x86_64.sh
#source ~/.bashrc
#
## install pangolin
#git clone git@github.com:cov-lineages/pangolin.git
#cd pangolin
#conda env create -f environment.yml
#conda activate pangolin
#python setup.py install
#
## check pangolin installation worked:
#pangolin -pv

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

# save the pangolin results back to the db:
/aspen/.venv/bin/python /aspen/src/backend/workflows/pangolin/save.py \
  --pangolin-input-file $lineage_report \

