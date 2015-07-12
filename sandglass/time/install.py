# pylint: disable=C0103
import transaction

from sandglass.time import _
from sandglass.time import security
from sandglass.time.models import DBSESSION
from sandglass.time.models import MODEL_REGISTRY
from sandglass.time.models import scan_models
from sandglass.time.models.group import Group
from sandglass.time.models.permission import Permission
from sandglass.time.security import PERMISSION


class PermissionManager(object):
    def __init__(self, session):
        self.instances = {}
        self.session = session
        self.create_instances()

    def create_instances(self):
        if not MODEL_REGISTRY:
            scan_models('sandglass.time.models')

        current_id = 1
        # Iterate all registered models
        for name, model in MODEL_REGISTRY.iteritems():
            if name.startswith('_'):
                continue

            # Get permissions for current model and create classes
            # for each permission.
            # When extra permissions are given add them also after
            # model permissions.
            permission_list = model.get_full_permission_list()
            extra_permissions = self.get_extra_permissions()
            if extra_permissions:
                permission_list.extend(extra_permissions)

            for permission_name in permission_list:
                permission = Permission(
                    id=current_id,
                    name=str(permission_name),
                    # TODO: Add a description for permissions
                    description=u'',
                )
                self.session.add(permission)
                self.instances[permission_name] = permission
                current_id += 1

    def get_extra_permissions(self):
        return (
            PERMISSION.get('api', 'describe'),
        )

    def get_permission(self, model_name, permission_name):
        """
        Get a permission for a model.

        AttributeError is raised when PermissionData does not have
        the permission defined as attribute.

        Returns a permission or None.

        """
        perm = PERMISSION.get(model_name, permission_name)
        return self.instances.get(perm)

    def get_permission_list(self, model_name, flags):
        """
        Get a list of permissions for a model.

        Returns a List of permissions.

        """
        permissions = []
        for perm in PERMISSION.cruda(model_name, flags=flags):
            permission = self.instances.get(perm)
            if permission and (permission not in permissions):
                permissions.append(permission)

        return permissions

    @property
    def users_group_permissions(self):
        return (
            self.get_permission_list('tag', 'cruda') +
            self.get_permission_list('group', 'r') +
            self.get_permission_list('permission', 'r') +
            self.get_permission_list('project', 'cruda') +
            self.get_permission_list('task', 'cruda') +
            self.get_permission_list('client', 'ra') +
            self.get_permission_list('user', 'ra') +
            self.get_permission_list('activity', 'cruda') +
            # Add non CRUDA permission(s)
            [self.et_permission('api', 'describe')]
        )

    @property
    def managers_group_permissions(self):
        return (
            self.users_group_permissions +
            self.get_permission_list('group', 'cuda') +
            self.get_permission_list('permission', 'ua') +
            self.get_permission_list('client', 'cud') +
            self.get_permission_list('user', 'cud') +
            # Add non CRUDA permission(s)
            [self.get_permission('project', 'set_is_public')]
        )


def database_insert_default_data(session=None, commit=True):
    """
    Insert initial database data.

    This must be called only once to setup initial database recods.

    """
    if not session:
        session = DBSESSION()

    manager = PermissionManager(session)

    # Add default groups
    session.add_all([
        Group(
            name=security.Administrators,
            description=_(u"Administrators"),
        ),
        Group(
            name=security.Users,
            description=_(u"Users"),
            permissions=manager.users_group_permissions,
        ),
        Group(
            name=security.Managers,
            description=_(u"Managers"),
            permissions=manager.managers_group_permissions,
        )
    ])

    if commit:
        transaction.commit()
