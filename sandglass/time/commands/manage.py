from __future__ import print_function

from cement.core import controller
from cement.core import handler

from sandglass.time import _


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

    @controller.expose(help="create a new user")
    def create_user(self):
        print(_("Create a new user") + u'\n')
        email = self.app.input(_("E-Mail"))
        first_name = self.app.input(_("First name"), default="")
        last_name = self.app.input(_("Last name"), default="")


handler.register(ManageController)
