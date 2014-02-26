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
        id = 1
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
        # Keep track of parsed models to avoid generating data
        # for a model registered with more than one name.
        # This happens, for example, during unittest because
        # fixtures "binds" dataset and model by registering
        # models under different names.
        parsed_model_list = []
        # Iterate all registered models
        for name, model in MODEL_REGISTRY.iteritems():
            if name.startswith('_') or model in parsed_model_list:
                continue
            else:
                parsed_model_list.append(model)

            # Get permissions for current model
            permission_list = model.get_default_permission_list()
            for permission in permission_list:
                data_item = (permission, {'name': str(permission)})
                data_list.append(data_item)

        return tuple(data_list)


# Datasets to be inserted in database during install
DEFAULT_DATASETS = (
    GroupData,
    PermissionData,
)


def database_insert_default_data():
    """
    Insert initial database data.

    This must be called only once to setup initial database recods.

    Returns a FixtureData.

    """
    fixture = SQLAlchemyFixture(
        env=MODEL_REGISTRY,
        engine=META.bind,
        style=NamedDataStyle())
    data = fixture.data(*DEFAULT_DATASETS)
    data.setup()
    return data
