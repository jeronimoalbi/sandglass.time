import getpass
import os
import sys

from ConfigParser import SafeConfigParser
from functools import wraps

from cement.core import controller
from cement.core import hook
from cement.core import foundation
from pyramid.config import Configurator
from venusian import Scanner

from sandglass.time import _


class BaseController(controller.CementBaseController):
    class Meta:
        label = 'base'
        description = _("Sandglass command line interface")
        config_section = 'cli:main'

    @controller.expose(hide=True, aliases=['help'])
    def default(self):
        self.app.args.parse_args(['--help'])


class SandglassCliApp(foundation.CementApp):
    class Meta:
        label = 'sandglass'
        base_controller = BaseController

    def scan_commands(self):
        """
        Scan and register all CLI commands.

        """
        import sandglass.time.commands

        # TODO: Implement support for commands in other applications
        scanner = Scanner()
        scanner.scan(sandglass.time.commands)

    def init_pylons_config(self, config_file):
        """
        Initialize Pylons related application configuration.

        """
        self.log.debug("Parsing config settings for Pylons")
        # Parse ini file using SafeConfigParser to add env vars
        full_path = os.path.abspath(config_file)
        defaults = {'here': os.path.dirname(full_path)}
        parser = SafeConfigParser(defaults)
        parser.read(full_path)
        # Use "app:main" section settings to initialize the application
        settings = dict(parser.items('app:main'))
        # Initialize pylons configurator
        self.log.debug("Initializing Pylons configurator")
        self._config = Configurator(settings=settings)
        self._config.include('sandglass.time.config')
        self._config.commit()

    @staticmethod
    def input(label, default=None, echo=True):
        """
        Get user input.

        Return a String.

        """
        if default is not None:
            text = "{0} [{1}]: ".format(label, default)
        else:
            text = "{}: ".format(label)

        if echo:
            value = raw_input(text).strip()
        else:
            value = getpass.getpass(text)

        if value:
            value = unicode(value, sys.stdin.encoding)

        return value or default


def database_command(func):
    """
    Command method decorator to setup Pyramid/database context before run.

    Methods that need to have Pyramid initialized before they run has to be
    wrapped with this decorator.

    """
    @wraps(func)
    def func_wrapper(self, *args, **kwargs):
        # Load config before running command
        config_file = self.app.pargs.config
        self.app.init_pylons_config(config_file)
        # Run the command
        return func(self, *args, **kwargs)

    return func_wrapper


def post_argument_parsing_hook(app):
    """
    Called after application arguments are parsed.

    """
    # Load application config
    config_file = app.pargs.config
    config_loaded = app.config.parse_file(config_file)
    if not config_loaded:
        msg = _("Config file {} could not be loaded").format(config_file)
        app.log.error(msg)
        sys.exit(1)
    else:
        msg = _("Using config file {}").format(config_file)
        app.log.debug(msg)


def main():
    """
    Main entry point for command line interface.

    """
    app = SandglassCliApp()
    hook.register('post_argument_parsing', post_argument_parsing_hook)

    try:
        app.scan_commands()
        # Prepare application
        app.setup()
        # Add global application arguments
        app.args.add_argument(
            '-c',
            '--config',
            action='store',
            metavar='FILE',
            help="sandglass config file",
            default='sandglass.ini')
        # Execute command line application
        app.run()
    finally:
        app.close()
