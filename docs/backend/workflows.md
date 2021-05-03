## Workflows

Aspen has a number of long-lived workflows that are run through AWS Batch.  This document explains each of these workflows and how to manually invoke them.

### Ingest GISAID

This workflow downloads a [GISAID hCov-19 data dump](https://www.gisaid.org/) and records a [`RawGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+RawGisaidDump%22) object referencing the dump.  This workflow can be manually invoked using the AWS cli: `aws batch submit-job --job-name 'ingest-gisaid' --job-queue aspen-batch --job-definition aspen-batch-job-definition --container-overrides '{"command": ["trunk", "src/backend/aspen/workflows/ingest_gisaid/ingest.sh"]}'`

This workflow automatically invokes the [transform-gisaid workflow](#transform-gisaid) upon completion, using the [`RawGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+RawGisaidDump%22) as input.

### Transform GISAID

This workflow applies the [transform-gisaid script](https://github.com/nextstrain/ncov-ingest/blob/master/bin/transform-gisaid) to transform the metadata into the format expected by the nextstrain pipeline.  The input for this workflow is a [`RawGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+RawGisaidDump%22) object and records a [`ProcessedGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+ProcessedGisaidDump%22) object referencing the processed dump.  A [`GisaidDumpWorkflow`](https://github.com/chanzuckerberg/aspen/search?q=%22class+GisaidDumpWorkflow%22) is used to link the input to the output.

This workflow automatically invokes the [align-gisaid workflow](#align-gisaid) upon completion, using the [`ProcessedGisaidDump`](../../src/backend/aspen/database/models/gisaid_dump.py) as input.

### Align GISAID

This workflow aligns the sequences downloaded from gisaid to a reference sequence, using the align step in the [nextstrain workflow](https://github.com/nextstrain/ncov/blob/master/workflow/snakemake_rules/main_workflow.smk).  The input for this workflow is a [`ProcessedGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+ProcessedGisaidDump%22) object and records an [`AlignedGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+AlignedGisaidDump%22) object referencing the aligned dump.  A [`GisaidAlignmentWorkflow`](https://github.com/chanzuckerberg/aspen/search?q=%22class+GisaidAlignmentWorkflow%22) is used to link the input to the output.

### Nextstrain

This workflow pulls the inputs for a [`PhyloRun`](https://github.com/chanzuckerberg/aspen/search?q=%22class+PhyloRun%22), which consists of [`UploadedPathogenGenome`](https://github.com/chanzuckerberg/aspen/search?q=%22class+UploadedPathogenGenome%22), [`CalledPathogenGenome`](https://github.com/chanzuckerberg/aspen/search?q=%22class+CalledPathogenGenome%22), and [`AlignedGisaidDump`](https://github.com/chanzuckerberg/aspen/search?q=%22class+AlignedGisaidDump%22).  It creates a builds file based on templates in [build_templates](../../src/backend/aspen/workflows/nextstrain_run/builds_templates/), and then kicks off a nextstrain run.

The input for this workflow is a [`PhyloRun`](https://github.com/chanzuckerberg/aspen/search?q=%22class+PhyloRun%22), and the output is a [`PhyloTree`](https://github.com/chanzuckerberg/aspen/search?q=%22class+PhyloTree%22) object.  This workflow can be manually invoked using the Aspen CLI: `aspen-cli db --remote create-phylo-run --group-name 'Orange County Public Health Lab'  --all-group-sequences --builds-template-file src/backend/aspen/workflows/nextstrain_run/builds_templates/group_plus_context.yaml --builds-template-args '{"division": "California", "location": "Orange County"}'`
