# pylint: disable=C0103

from fixture import DataSet
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

from sandglass.time import _
from sandglass.time import security
from sandglass.time.models import META
from sandglass.time.models import MODEL_REGISTRY
from sandglass.time.models import scan_models
from sandglass.time.security import PERMISSION


def model_permission_data_class_factory(cls_name, extra_permissions=None):
    """
    Create DataSet class with all registered models permissions.

    Extra permission names can be given as a list using `extra_permissions`
    argument.

    Returns a DataSet class.

    """
    if not MODEL_REGISTRY:
        scan_models('sandglass.time.models')

    current_id = 1
    attrs = {}
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

        # Get permissions for current model and create classes
        # for each permission. Each class will be assigned to
        # the new "DataSet" class being created.
        # When extra permissions are given add them also after
        # model permissions.
        permission_list = model.get_full_permission_list()
        if extra_permissions:
            permission_list.extend(extra_permissions)

        for permission in permission_list:
            inner_cls_name = permission
            fields = {
                'id': current_id,
                'name': str(permission),
                # TODO: Add a description for permissions
                'description': u'',
            }
            attrs[inner_cls_name] = type(inner_cls_name, (), fields)
            current_id += 1

    return type(cls_name, (DataSet, ), attrs)


# Dataset with all model permissions.
PermissionData = model_permission_data_class_factory(
    'PermissionData',
    extra_permissions=(
        PERMISSION.get('api', 'describe'),
    )
)


def get_permission(model_name, permission_name):
    """
    Get a permission for a model.

    AttributeError is raised when PermissionData does not have
    the permission defined as attribute.

    Returns a permission.

    """
    perm = PERMISSION.get(model_name, permission_name)
    return getattr(PermissionData, perm)


def get_permission_list(model_name, flags):
    """
    Get a list of permissions for a model.

    Returns a List of permissions.

    """
    permissions = []
    for perm in PERMISSION.cruda(model_name, flags=flags):
        permission = getattr(PermissionData, perm, None)
        if permission and (permission not in permissions):
            permissions.append(permission)

    return permissions


USERS_GROUP_PERMISSIONS = (
    get_permission_list('tag', 'cruda') +
    get_permission_list('group', 'r') +
    get_permission_list('permission', 'r') +
    get_permission_list('project', 'cruda') +
    get_permission_list('task', 'cruda') +
    get_permission_list('client', 'ra') +
    get_permission_list('user', 'ra') +
    get_permission_list('activity', 'cruda') +
    # Add non CRUDA permission(s)
    [get_permission('api', 'describe')]
)


MANAGERS_GROUP_PERMISSIONS = (
    USERS_GROUP_PERMISSIONS +
    get_permission_list('group', 'cuda') +
    get_permission_list('permission', 'ua') +
    get_permission_list('client', 'cud') +
    get_permission_list('user', 'cud') +
    # Add non CRUDA permission(s)
    [get_permission('project', 'set_is_public')]
)


class GroupData(DataSet):
    """
    Dataset with Group data.

    """
    class Admins:
        name = security.Administrators
        id = 1
        description = _(u"Administrators")

    class Users:
        name = security.Users
        id = 2
        description = _(u"Users")
        permissions = USERS_GROUP_PERMISSIONS

    class Managers:
        name = security.Managers
        id = 3
        description = _(u"Managers")
        permissions = MANAGERS_GROUP_PERMISSIONS


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
