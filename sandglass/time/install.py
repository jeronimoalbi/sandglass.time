from fixture import DataSet
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

from sandglass.time import _
from sandglass.time.models import BaseModel
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


class PermissionData(DataSet):
    """
    Dataset with all model permissions.

    """
    def data(self):
        """
        Generate Dataset data.

        """
        data_list = []
        # Iterate all registered models
        for name, model in MODEL_REGISTRY.iteritems():
            if name.startswith('_'):
                continue

            # Get permissions for current model
            permission_list = model.get_default_permission_list()
            for permission in permission_list:
                data_item = (permission, {'name': str(permission)})
                data_list.append(data_item)

        return tuple(data_list)


def database_insert_default_data():
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
        PermissionData,
    )
    data.setup()
