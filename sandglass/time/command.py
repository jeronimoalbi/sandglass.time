from __future__ import print_function

import sys

from cement.core import controller
from cement.core import hook
from cement.core import foundation
from venusian import Scanner

from sandglass.time import _


class BaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = _("Sandglass command line interface")
        # TODO: Use 'cli:main' ?
        config_section = 'app:main'
        arguments = [
            (['-c', '--config'], dict(
                action='store',
                metavar='FILE',
                help="sandglass config file",
                default='sandglass.ini',
            )),
        ]

    @controller.expose(hide=True)
    def default(self):
        self.app.args.parse_args(['--help'])


class SandglassCliApp(foundation.CementApp):
    class Meta:
        label = 'sandglass'
        base_controller = BaseController

    def scan_commands(self):
        """
        Scan all command controllers.

        """
        import sandglass.time.commands
        # Scan commands
        # TODO: Implement support for commands in other applications
        scanner = Scanner()
        scanner.scan(sandglass.time.commands)


def post_setup_hook(app):
    """
    Called after application setup is called.

    """
    # Load application config
    config_file = app.pargs.config
    config_loaded = app.config.parse_file(config_file)
    if not config_loaded:
        msg = _("Config file {} could not be loaded").format(config_file)
        print(msg)
        sys.exit(1)
    else:
        msg = _("Using config file {}").format(config_file)
        print (msg)


def main():
    """
    Main entry point for command line interface.

    """
    hook.register('post_setup', post_setup_hook)

    try:
        app = SandglassCliApp()
        app.scan_commands()

        # Prepare application
        app.setup()
        # Execute command line application
        app.run()
    finally:
        app.close()
