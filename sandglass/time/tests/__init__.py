import os
import unittest

from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from sqlalchemy.orm import sessionmaker
from webtest import TestApp
from zope.sqlalchemy import ZopeTransactionExtension


def get_static_test_dir():
    """
    Get path to static files directory for tests.

    Static directory contains all non python files needed
    for the tests to be run.

    Return a String with the directory path.

    """
    tests_dir = os.path.dirname(__file__)
    return os.path.join(tests_dir, 'static')


def get_config_file_path():
    """
    Get path to tests config file `sandglass-tests.ini`
    """
    file_name = 'sandglass-tests.ini'
    tests_dir = os.path.dirname(__file__)
    file_path = [tests_dir, os.pardir, os.pardir, os.pardir, file_name]
    return os.path.join(*file_path)


# Load tests settings
SETTINGS = appconfig('config:' + get_config_file_path())


class BaseTestCase(unittest.TestCase):
    """
    Base class for all tests.

    """
    @classmethod
    def setUpClass(cls):
        from sandglass.time import models
        from sandglass.time.models import META

        # Make global database session a non scoped session
        models.DBSESSION = sessionmaker(extension=ZopeTransactionExtension())

        # Initialize some useful class variables
        # to be available in all test classes
        cls.meta = META
        cls.Session = models.DBSESSION
        cls.settings = SETTINGS

    @staticmethod
    def _initialize_wsgi_application():
        """
        Initialize WSGI application instance.

        Return a WSGI application.

        """
        from sandglass.time.main import make_wsgi_app

        print "Initializing WSGI test application ..."
        return make_wsgi_app({}, **SETTINGS)

    def setUp(self):
        request = testing.DummyRequest()
        # Call pyramid setUp, and later on tearDown to properly
        # support 'get_current_*' functions or calls Pyramid
        # code uses to that function.
        # Also give a request to avoid getting None during
        # 'pyramid.threadlocal.get_current_request()'
        self.config = testing.setUp(request=request)

    def tearDown(self):
        testing.tearDown()


class UnitTestCase(BaseTestCase):
    """
    Base class for unit tests.

    Unit tests are small tests that only test 1 thing at a time.

    Test WSGI application can be accesed as `self.app`.

    """
    def setUp(self):
        super(UnitTestCase, self).setUp()
        self.wsgi_app = self._initialize_wsgi_application()
        self.app = TestApp(self.wsgi_app)

    def tearDown(self):
        super(UnitTestCase, self).tearDown()
        print "Dropping all database tables ..."
        self.meta.drop_all()


class FunctionalTestCase(BaseTestCase):
    """
    Base class for functional tests.

    This will integrate with the whole web framework and test
    the full stack of your application.

    Test WSGI application can be accesed as `self.app`.

    """
    @classmethod
    def setUpClass(cls):
        super(FunctionalTestCase, cls).setUpClass()
        cls.wsgi_app = cls._initialize_wsgi_application()
        cls.app = TestApp(cls.wsgi_app)

    @classmethod
    def tearDownClass(cls):
        super(FunctionalTestCase, cls).tearDownClass()
        # Drop all tables and data
        cls.meta.drop_all()

    def _create(self, path, content=None, status=200):
        create_response = self.app.post_json(path, content, status=status)
        created_id = create_response.json[0]['id']
        json = create_response.json

        return (created_id, json)
