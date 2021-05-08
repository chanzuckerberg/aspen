import datetime
import io
import json
from typing import MutableSequence, Set

import click
from sqlalchemy.orm import joinedload

from aspen.config.config import Config
from aspen.database.connection import (
    get_db_uri,
    init_db,
    session_scope,
    SqlAlchemyInterface,
)
from aspen.database.models import (
    CallConsensus,
    CalledPathogenGenome,
    FilterRead,
    HostFilteredSequencingReadsCollection,
    PathogenGenome,
    PhyloRun,
    PhyloTree,
    Sample,
    SequencingReadsCollection,
    UploadedPathogenGenome,
)
from aspen.database.models.workflow import SoftwareNames, WorkflowStatusType
from aspen.phylo_tree.identifiers import get_names_from_tree


@click.command("save")
@click.option("--aspen-workflow-rev", type=str, required=True)
@click.option("--aspen-creation-rev", type=str, required=True)
@click.option("--ncov-rev", type=str, required=True)
@click.option("--aspen-docker-image-version", type=str, required=True)
@click.option("--end-time", type=int, required=True)
@click.option("--phylo-run-id", type=int, required=True)
@click.option("--bucket", type=str, required=True)
@click.option("--key", type=str, required=True)
@click.option("--tree-path", type=click.File("r"), required=True)
def cli(
    aspen_workflow_rev: str,
    aspen_creation_rev: str,
    ncov_rev: str,
    aspen_docker_image_version: str,
    end_time: int,
    phylo_run_id: int,
    bucket: str,
    key: str,
    tree_path: io.TextIOBase,
):
    end_time_datetime = datetime.datetime.fromtimestamp(end_time)

    interface: SqlAlchemyInterface = init_db(get_db_uri(Config()))
    with session_scope(interface) as session:
        phylo_run: PhyloRun = (
            session.query(PhyloRun)
            .filter(PhyloRun.workflow_id == phylo_run_id)
            .options(
                joinedload(PhyloRun.inputs.of_type(UploadedPathogenGenome))
                # load the sample that this uploaded pathogen genome was associated with
                .subqueryload(UploadedPathogenGenome.sample),
                joinedload(PhyloRun.inputs.of_type(CalledPathogenGenome))
                # load the workflows that generated the consensus calls.
                .subqueryload(
                    CalledPathogenGenome.producing_workflow.of_type(CallConsensus)
                )
                # load the host-filtered sequencing reads that generated the called
                # pathogen genomes.
                .subqueryload(
                    CallConsensus.inputs.of_type(HostFilteredSequencingReadsCollection)
                )
                # load the workflows that generated the host-filtered sequencing
                # reads.
                .subqueryload(
                    HostFilteredSequencingReadsCollection.producing_workflow.of_type(
                        FilterRead
                    )
                )
                # load the sequencing reads that generated the host-filtered
                # sequencing reads.
                .subqueryload(FilterRead.inputs.of_type(SequencingReadsCollection))
                # load the samples that the sequencing reads collection was associated
                # with.
                .subqueryload(SequencingReadsCollection.sample),
            )
            .one()
        )

        assert phylo_run.workflow_status != WorkflowStatusType.COMPLETED

        # read the tree
        tree_json = json.load(tree_path)
        all_public_identifiers = get_names_from_tree([tree_json["tree"]])

        # get all the children that are pathogen genomes
        pathogen_genomes = [
            inp for inp in phylo_run.inputs if isinstance(inp, PathogenGenome)
        ]

        uploaded_pathogen_genomes: Set[UploadedPathogenGenome] = {
            pathogen_genome
            for pathogen_genome in pathogen_genomes
            if isinstance(pathogen_genome, UploadedPathogenGenome)
        }
        sequencing_reads_collections: Set[SequencingReadsCollection] = {
            pathogen_genome.get_parents(HostFilteredSequencingReadsCollection)[
                0
            ].get_parents(SequencingReadsCollection)[0]
            for pathogen_genome in pathogen_genomes
            if isinstance(pathogen_genome, CalledPathogenGenome)
        }

        included_samples: MutableSequence[Sample] = list()
        for uploaded_pathogen_genome in uploaded_pathogen_genomes:
            if (
                uploaded_pathogen_genome.sample.public_identifier
                in all_public_identifiers
            ):
                included_samples.append(uploaded_pathogen_genome.sample)
        for sequencing_reads_collection in sequencing_reads_collections:
            if (
                sequencing_reads_collection.sample.public_identifier
                in all_public_identifiers
            ):
                included_samples.append(sequencing_reads_collection.sample)

        # create an output
        phylo_tree = PhyloTree(
            s3_bucket=bucket,
            s3_key=key,
            constituent_samples=included_samples,
        )

        # update the run object with the metadata about the run.
        phylo_run.end_datetime = end_time_datetime
        phylo_run.workflow_status = WorkflowStatusType.COMPLETED
        phylo_run.software_versions = {
            SoftwareNames.ASPEN_WORKFLOW: aspen_workflow_rev,
            SoftwareNames.ASPEN_CREATION: aspen_creation_rev,
            SoftwareNames.NCOV: ncov_rev,
            SoftwareNames.ASPEN_DOCKER_IMAGE: aspen_docker_image_version,
        }
        phylo_run.outputs = [phylo_tree]


if __name__ == "__main__":
    cli()
