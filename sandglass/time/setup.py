from fixture import DataSet
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

from sandglass.time import _
from sandglass.time.models import META
from sandglass.time.models import MODEL_REGISTRY
from sandglass.time.security import Administrators


class GroupData(DataSet):
    """
    Dataset with Group data.

    """
    class Admins:
        name = Administrators
        description = _("Administrators")


def init_database_data():
    """
    Insert initial database data.

    This must be called only once to setup initial database recods.

    """
    db_fixture = SQLAlchemyFixture(
        env=MODEL_REGISTRY,
        engine=META.bind,
        style=NamedDataStyle())
    # Register Datasets to be created
    data = db_fixture.data(
        GroupData,
    )
    data.setup()
