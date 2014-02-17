from __future__ import print_function

import sys

import transaction

from cement.core import controller
from cement.core import handler

from sandglass.time import _
from sandglass.time import setup
from sandglass.time.utils import is_valid_email
from sandglass.time.models.user import User
from sandglass.time.models.group import Group
from sandglass.time.security import Administrators


class ManageController(controller.CementBaseController):
    """
    Sandglass CLI command to manage application data.

    """
    class Meta:
        label = 'manage'
        interface = controller.IController
        description = "Manage application data"
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['-a', '--admin'], dict(
                action='store_true',
                help="user is an administrator",
            )),
        ]

    @controller.expose(help="insert initial application data")
    def init_database(self):
        """
        Insert initial database records to a newly created database.

        """
        setup.init_database_data()
        print(_("Sandglass is ready to run now"))

    @controller.expose(help="create a new user")
    def create_user(self):
        """
        Create a new user.

        """
        print(_("Create a new user"), '\n')
        email = self.app.input(_("E-Mail"))
        if not is_valid_email(email):
            self.app.log.error(_("E-Mail address is not valid"))
            sys.exit(1)

        if User.query().filter_by(email=email).count():
            self.app.log.error(_("A user with same E-Mail already exists"))
            sys.exit(1)

        data = {}
        data['email'] = email
        data['first_name'] = self.app.input(_("First name"))
        data['last_name'] = self.app.input(_("Last name"))
        if not (data['first_name'] and data['last_name']):
            self.app.log.error(_("User first and last names are mandatory"))

        user = User(**data)
        session = user.new_session()
        session.add(user)

        # When user is an admin add it to admins group
        if self.app.pargs.admin:
            admin_group = Group.query().filter_by(name=Administrators).first()
            if not admin_group:
                print(_("Administrators group is not defined"))
                transaction.doom()
                sys.exit(1)

            user.groups.append(admin_group)

        # Print token and key after creation
        msg = _("Token: {0}\nKey: {1}").format(user.token, user.key)
        print(msg, '\n')

        transaction.commit()
        print('\n', _("User created successfully"))


handler.register(ManageController)