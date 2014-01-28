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
    @classmethod
    def setUpClass(self):
        self.app = run_wsgi(TEST_SETTINGS, **TEST_SETTINGS)

        self.testapp = TestApp(self.app)

    @classmethod
    def tearDownClass(self):
        # Clear database of all models

        # Delete all users
        self.testapp.delete_json(
            '/time/api/v1/users/', status=200)

        # Delete all clients
        self.testapp.delete_json(
            '/time/api/v1/clients/', status=200)

    def _create(self, path, content=None, status=200):
        create_response = self.testapp.post_json(path, content, status=status)
        created_id = create_response.json[0]['id']
        json = create_response.json

        return (created_id, json)
