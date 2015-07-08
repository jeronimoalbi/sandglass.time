import os

# Set TESTING environmental variable as soon as test is imported
os.environ['TESTING'] = 'true'

import base64
import warnings

import pytest

from fixture import SQLAlchemyFixture
from fixture import DataSet
from fixture.style import NamedDataStyle
from paste.deploy.loadwsgi import appconfig
from pyramid import testing
from webtest import lint
from webtest import TestApp

from sandglass.time import models
from sandglass.time.models import META
from sandglass.time.models import MODEL_REGISTRY
from sandglass.time.install import DEFAULT_DATASETS
from sandglass.time.install import GroupData


# Filter WebTest warnings regarding WSGI
warnings.filterwarnings('ignore', category=lint.WSGIWarning)

# Scan sandglass time models to for registration
# before FIXTURE_ENV is initialized
models.scan_models('sandglass.time.models')

# Init fixture to database mappings environment.
# This registers all current Model definitions to
# be vailable for the fixtures.
FIXTURE_ENV = MODEL_REGISTRY
FIXTURE_ENV.update({
    'AdminUser': MODEL_REGISTRY['User'],
})

# API HTTP basic authorization token and key for admin test user
AUTH_TOKEN = "058bb38b25ddefa3f20537fd8762633dd2c3472f36f9b6628662624fffc7cbc2"
AUTH_KEY = "56f750326fe58c2266e864d4cd95c6ea2877ce9aa5da0b73ef57f2e8774433a4"


class AdminUserData(DataSet):
    """
    Fixture dataset with test admin user definitions.

    """
    class Admin(object):
        id = 1
        first_name = u"Admin"
        last_name = u"User"
        email = u"admin@sandglass.net"
        password = "1234"
        token = AUTH_TOKEN
        key = AUTH_KEY
        salt = "a66a328e85e9d74da8dac441cb6f5578c530c70f"
        groups = [GroupData.Admins]


class RequestHelper(object):
    def __init__(self, app):
        self.app = app
        # By default add HTTP auth headers for all requests
        self.require_authorization = True

    @staticmethod
    def get_authorization_header():
        """
        Get HTTP basic auth headers for current token and key.

        Returns a Dictionary.

        """
        header = {}
        auth_string = "{}:{}".format(AUTH_TOKEN, AUTH_KEY)
        auth_string_enc = base64.b64encode(auth_string)
        header['Authorization'] = "Basic {}".format(auth_string_enc)
        return header

    def update_headers(self, headers):
        """
        Update request headers dictionary.

        This is an entry point for tests to override/add/delete
        special HTTP request headers.

        Return a Dictionary.

        """
        if not headers:
            headers = {}

        # Add content type, to force application request
        # to use JSON when no body data is available.
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        # Add basig HTTP authorization information
        if self.require_authorization:
            authorization_header = self.get_authorization_header()
            headers.update(authorization_header)

        return headers

    def get_json(self, *args, **kwargs):
        """
        Make a GET request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        if 'expect_errors' not in kwargs:
            kwargs['expect_errors'] = True

        return self.app.get(*args, **kwargs)

    def post_json(self, *args, **kwargs):
        """
        Make a JSON POST request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        if 'expect_errors' not in kwargs:
            kwargs['expect_errors'] = True

        return self.app.post_json(*args, **kwargs)

    def put_json(self, *args, **kwargs):
        """
        Make a JSON PUT request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        if 'expect_errors' not in kwargs:
            kwargs['expect_errors'] = True

        return self.app.put_json(*args, **kwargs)

    def delete_json(self, *args, **kwargs):
        """
        Make a JSON DELETE request to the application.

        Return a response.

        """
        kwargs['headers'] = self.update_headers(kwargs.get('headers'))
        if 'expect_errors' not in kwargs:
            kwargs['expect_errors'] = True

        return self.app.delete_json(*args, **kwargs)


@pytest.fixture(scope='session')
def static_dir():
    """
    Get path to static files directory for tests.

    Static directory contains all non python files needed
    for the tests to be run.

    Return a String with the directory path.

    """
    tests_dir = os.path.dirname(__file__)
    return os.path.join(tests_dir, 'static')


@pytest.fixture(scope='session')
def settings():
    file_name = 'sandglass-tests.ini'
    cwd_path = os.getcwd()
    file_path = os.path.join(cwd_path, file_name)
    config_file_path = os.path.join(file_path)
    return appconfig('config:{}'.format(config_file_path))


@pytest.fixture(scope='function')
def config(request, settings):
    def teardown_config():
        META.drop_all()
        # Clear all table data to avoid conflicts when using fixtures
        # and to start next test with a clean database
        #models.clear_tables()
        testing.tearDown()

    # Set Pyramid registry and request thread locals
    # for the duration of a single unit test.
    conf = testing.setUp(
        settings=settings,
        autocommit=True,
        request=testing.DummyRequest(),
    )
    conf.include('sandglass.time.config')
    request.addfinalizer(teardown_config)
    return conf


@pytest.fixture(scope='function')
def fixture(request):
    def teardown_fixture():
        if manager.loaded:
            manager.unload()

    style = NamedDataStyle()
    manager = SQLAlchemyFixture(env=FIXTURE_ENV, style=style, engine=META.bind)
    request.addfinalizer(teardown_fixture)
    return manager


@pytest.fixture(scope='function')
def default_data(request, fixture):
    # Add authorization data to defaults
    datasets = list(DEFAULT_DATASETS)
    datasets.append(AdminUserData)
    # Insert default data into database
    data = fixture.data(*datasets)
    data.setup()
    return data


@pytest.fixture(scope='function')
def app(config):
    wsgi_app = config.make_wsgi_app()
    return TestApp(wsgi_app)


@pytest.fixture(scope='function')
def request_helper(app):
    return RequestHelper(app=app)
