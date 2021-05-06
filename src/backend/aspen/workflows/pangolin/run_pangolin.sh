#set -Eex pipefail

# install miniconda
eval "$($HOME/miniconda/bin/conda shell.bash hook)"
conda init

# install pangolin
#mkdir pangolin
#cd pangolin
#git init
#git fetch --depth 1 git://github.com/cov-lineages/pangolin.git
#git checkout FETCH_HEAD
#conda env create -f environment.yml
conda activate pangolin
#python setup.py install

# check pangolin installation worked:
#pangolin -pv

# process all trailing args to include --sample-public-identifiers flag
echo "${@}"

args=""
for sample_id in "${@}"
do
    args="$args --sample-public-identifier $sample_id"
done

sequences_output="sequences.fasta"

# call export script to export renamed sequences
/usr/local/bin/python3.9 export.py \
  $args \
  --sequences "$sequences_output"

# call pangolin on the exported sequences
lineage_report="lineage_report.csv"
pangolin $sequences_output --outfile "$lineage_report"

last_updated=$(date +'%m-%d-%Y')
# save the pangolin results back to the db:
/usr/local/bin/python3.9 save.py \
  --pangolin-csv "$lineage_report" \
  --pangolin-last-updated "$last_updated"