from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref, relationship

from aspen.database.models.base import base
from aspen.database.models.entity import Entity, EntityType
from aspen.database.models.sample import Sample
from aspen.database.models.usergroup import Group
from aspen.database.models.workflow import Workflow, WorkflowType

_PHYLO_TREE_TABLENAME = "phylo_trees"


PhyloTreeSamples = Table(
    "phylo_tree_samples",
    base.metadata,  # type: ignore
    Column("sample_id", ForeignKey(Sample.id), primary_key=True),
    Column(
        "phylo_tree_id",
        ForeignKey(f"{_PHYLO_TREE_TABLENAME}.entity_id"),
        primary_key=True,
    ),
)
"""This table records which samples are included in the phylo tree.  Note that this is
different from which samples are inputs into the build that creates a phylo tree."""


class PhyloTree(Entity):
    __tablename__ = _PHYLO_TREE_TABLENAME
    __table_args__ = (UniqueConstraint("s3_bucket", "s3_key"),)
    __mapper_args__ = {"polymorphic_identity": EntityType.PHYLO_TREE}

    entity_id = Column(Integer, ForeignKey(Entity.id), primary_key=True)

    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)

    constituent_samples = relationship(  # type: ignore
        Sample,
        secondary=PhyloTreeSamples,
        backref="phylo_trees",
        uselist=True,
    )


class PhyloRun(Workflow):
    __tablename__ = "phylo_runs"
    __mapper_args__ = {"polymorphic_identity": WorkflowType.PHYLO_RUN}

    workflow_id = Column(Integer, ForeignKey(Workflow.id), primary_key=True)
    group_id = Column(
        Integer,
        ForeignKey(Group.id),
        nullable=False,
    )
    group = relationship(Group, backref=backref("phylo_runs", uselist=True))  # type: ignore

    template_file_path = Column(String, nullable=True)
    """This is the path, relative to aspen root, for the builds template file.  For all
    new builds, this should be set.  However, for runs imported from covidhub, this
    would not be available."""

    template_args = Column(
        JSONB,
        nullable=False,
        default=text("'{}'::jsonb"),
        server_default=text("'{}'::jsonb"),
    )
    """The arguments, in conjunction with the template file, used to produce the final
    builds file."""

    template_file_path = Column(String, nullable=True)
    """This is the path, relative to aspen root, for the builds template file.  For all
    new builds, this should be set.  However, for historically imported """

    template_args = Column(
        JSONB,
        nullable=False,
        default=text("'{}'::jsonb"),
        server_default=text("'{}'::jsonb"),
    )
    """The arguments, in conjunction with the template file, used to produce the final
    builds file."""

    def tree(self) -> PhyloTree:
        """Find the tree resulting from this workflow."""
        for output in self.outputs:
            if isinstance(output, PhyloTree):
                return output
        raise ValueError(
            f"No phylo tree was generated from this workflow (id={self.id}."
        )
