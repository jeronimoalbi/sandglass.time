import os
import unittest

from paste.deploy import loadapp
from paste.deploy.loadwsgi import appconfig

from pyramid import testing
from sandglass.time.main import run_wsgi
from webtest import TestApp
from sandglass.time.models import user


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


def get_config_file_path():
    test_dir = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(test_dir,
                                    os.pardir, os.pardir, os.pardir,
                                    'sandglass-test.ini')

    return config_file_path


settings = appconfig('config:' + get_config_file_path())


from sandglass.time import models
from sandglass.time.models import META
from fixture import SQLAlchemyFixture
from fixture.style import NamedDataStyle

from sqlalchemy import engine_from_config

engine = engine_from_config(settings, prefix='database.')

from fixture import DataSet


class UserData(DataSet):

    class homer_simpson:
        email = "homer@simpson.com"
        first_name = "Homer"
        last_name = "Simpson"

    class marge_simpson:
        email = "marge@simpson.com"
        first_name = "marge"
        last_name = "Simpson"


dbfixture = SQLAlchemyFixture(
    env={'UserData': models.user.User, },
    engine=engine,
    style=NamedDataStyle()
)


# Test Base Classes
class BaseTest(unittest.TestCase):

    """
    Base class for functional test

    Creates testapp instance by wrapping main.run_wsgi()
    """

    def setUp(self):
        self.app = run_wsgi(TEST_SETTINGS, **TEST_SETTINGS)

        self.testapp = TestApp(self.app) 
        print "Setting settings..."
        self.settings = settings
        print "META create_all..."
        META.create_all(engine)

        self.data = dbfixture.data(UserData)
        self.data.setup()

        print "wsgiapp loadapp with config..."
        wsgiapp = loadapp('config:%s' % get_config_file_path())

        print "TestApp..."
        self.testapp = TestApp(wsgiapp)

    def tearDown(self):
        self.data.teardown()
        print "META drop_all..."
        META.drop_all(engine)

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
