import unittest

from pyramid import testing
from sandglass.time.main import run_wsgi
from webtest import TestApp

# TODO import these from an ini file
TEST_SETTINGS = {"use": "egg:sandglass.time",
                 "pyramid.reload_templates": "true",
                 "pyramid.debug_authorization": "false",
                 "pyramid.debug_notfound": "false",
                 "pyramid.debug_routematch": "false",
                 "pyramid.debug_templates": "true",
                 "pyramid.default_locale_name": "en",
                 "pyramid.includes": "pyramid_tm pyramid_mailer",
                 "available_languages": "en de es",
                 "tm.attempts": "3",
                 "mail.host": "localhost",
                 "mail.port": "25",
                 "database.url": "sqlite:///./sandglass_test.db",
                 "database.encoding": "utf8",
                 "database.echo": "false",
                }

# Test Base Classes

class BaseFunctionalTest(unittest.TestCase):
    """
    Base class for functional test

    Creates testapp instance by wrapping main.run_wsgi()
    """
    def setUp(self):

        self.app = run_wsgi(TEST_SETTINGS, **TEST_SETTINGS)

        self.testapp = TestApp(self.app)