from sqlalchemy.orm import Session

from aspen.database.models import CanSee, DataType, Group


def test_can_see_constructor_with_datatype(session: Session):
    """Test that we can construct a CanSee object with a `data_type` argument."""
    group1 = Group(name="group1", address="address1")
    group2 = Group(name="group2", address="address2")
    can_see = CanSee(viewer_group=group1, owner_group=group2, data_type=DataType.TREES)

    session.add_all((group1, group2, can_see))
    session.flush()

    assert can_see.data_type == DataType.TREES


def test_can_see_datatype_filter(session: Session):
    """Test that we can filter by the datatype."""
    group1 = Group(name="group1", address="address1")
    group2 = Group(name="group2", address="address2")
    can_see = CanSee(
        viewer_group=group1,
        owner_group=group2,
        data_type=DataType.TREES,
    )

    session.add_all((group1, group2, can_see))
    session.flush()

    session.query(CanSee).filter(CanSee.data_type == DataType.TREES).one()
