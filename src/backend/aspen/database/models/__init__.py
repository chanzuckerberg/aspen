from sqlalchemy.orm import configure_mappers

from aspen.database.models.accessions import (  # noqa: F401
    Accession,
    AccessionWorkflow,
    PublicRepositoryType,
)
from aspen.database.models.align_read import AlignRead, Bam  # noqa: F401
from aspen.database.models.base import meta  # noqa: F401
from aspen.database.models.cansee import CanSee, DataType  # noqa: F401
from aspen.database.models.entity import Entity, EntityType  # noqa: F401
from aspen.database.models.gisaid_dump import (  # noqa: F401
    AlignedGisaidDump,
    GisaidAlignmentWorkflow,
    GisaidDumpWorkflow,
    ProcessedGisaidDump,
    RawGisaidDump,
)
from aspen.database.models.host_filtering import (  # noqa: F401
    FilterRead,
    HostFilteredSequencingReadsCollection,
)
from aspen.database.models.phylo_tree import PhyloRun, PhyloTree  # noqa: F401
from aspen.database.models.sample import RegionType, Sample  # noqa: F401
from aspen.database.models.sequences import (  # noqa: F401
    CallConsensus,
    CalledPathogenGenome,
    PathogenGenome,
    SequencingInstrumentType,
    SequencingProtocolType,
    SequencingReadsCollection,
    UploadedPathogenGenome,
)
from aspen.database.models.usergroup import Group, User  # noqa: F401
from aspen.database.models.workflow import Workflow  # noqa: F401
from aspen.database.models.workflow import (  # noqa: F401
    WorkflowInputs,
    WorkflowStatusType,
    WorkflowType,
)

configure_mappers()
