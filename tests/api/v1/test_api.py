import pytest

from pyramid.testing import DummyRequest

from sandglass.time.api import ApiDescribeResource
from sandglass.time.api import ApiManager
from sandglass.time.api.error import APIError
from sandglass.time.api.v1.user import UserResource
from sandglass.time.request import rest_collection_mode
from sandglass.time.resource.base import BaseResource
from sandglass.time.utils import get_settings

USER_LIST = [
    {
        'email': 'api.test@sandglass.net',
        'first_name': 'API',
        'last_name': 'Test',
        'password': 'test'
    },
    {
        'email': 'api.test.2@sandglass.net',
        'first_name': 'API',
        'last_name': 'Test 2',
        'password': 'test',
    },
]


def test_api_describe_resource_class():
    class DescribeResource(ApiDescribeResource):
        version = 'invalid_version'

    request = DummyRequest()

    # When API version does not exist an exception is raised
    with pytest.raises(Exception):
        DescribeResource(request)

    # Otherwise resource can be created
    DescribeResource.version = 'v1'
    resource = DescribeResource(request)
    with pytest.raises(NotImplementedError):
        resource.describe()


def test_api_manager():
    class TestResource(BaseResource):
        name = 'tests'

    request = DummyRequest()
    manager = ApiManager(versions=['v1', 'v1.1', 'v2'])
    resource = TestResource(request)
    # Check that adding a resource works
    manager.register('v1.1', resource)
    assert resource in manager.get_resources('v1.1')
    # Resource should not be available for other API version
    assert resource not in manager.get_resources('v1')

    # Try to add a resource to an invalid API version
    assert not manager.register('invalid_version', resource)


def test_api_error():
    message = "A message"
    error = APIError('CODE', msg=message)
    assert error.msg == message
    # Check that default message is used when no message is given
    error = APIError('CODE')
    assert error.msg == APIError.default_msg


def test_get_rest_collection_mode(config):
    """
    Check REST collection mode request property.

    """
    request = DummyRequest()
    settings = get_settings()
    # Remove default value is is setted
    if 'request.rest_collection_mode' in settings:
        del settings['request.rest_collection_mode']

    # Check that mode is getted from request headers
    request.headers['X-REST-Collection-Mode'] = 'permissive'
    assert rest_collection_mode(request) == 'permissive'
    request.headers['X-REST-Collection-Mode'] = 'strict'
    assert rest_collection_mode(request) == 'strict'

    # Setting an invalid value should return a default value
    request.headers['X-REST-Collection-Mode'] = 'INVALID'
    # .. when no default exists in settings 'strict' is used as default
    assert rest_collection_mode(request) == 'strict'
    # .. or if there is a default then it is used instead
    settings['request.rest_collection_mode'] = 'permissive'
    assert rest_collection_mode(request) == 'permissive'

    # Finally remove setting to avoid messing with other tests
    del settings['request.rest_collection_mode']


@pytest.mark.usefixtures('default_data')
def test_strict_rest_collection_mode(request_helper):
    headers = {'X-REST-Collection-Mode': 'strict'}
    user = USER_LIST[0]
    url = UserResource.get_collection_path()

    # Mode strict should fail when no collection is sent
    response = request_helper.post_json(url, user, headers=headers)
    assert response.status_int == 400
    response_data = response.json_body
    assert 'error' in response_data
    assert 'code' in response_data['error']
    assert response_data['error']['code'] == 'COLLECTION_EXPECTED'

    # When a collection is sent is should work and return a collection
    response = request_helper.post_json(url, [user], headers=headers)
    assert response.status_int == 200
    assert isinstance(response.json_body, list)


@pytest.mark.usefixtures('default_data')
def test_permissive_rest_collection_mode(request_helper):
    headers = {'X-REST-Collection-Mode': 'permissive'}
    url = UserResource.get_collection_path()

    # Mode permissive should not fail when no collection is sent
    # and it should return an object when an object is sent
    user = USER_LIST[0]
    response = request_helper.post_json(url, user, headers=headers)
    assert response.status_int == 200
    assert isinstance(response.json_body, dict)

    # Mode permissive should return a list when a list is sent
    user = USER_LIST[1]
    response = request_helper.post_json(url, [user], headers=headers)
    assert response.status_int == 200
    assert isinstance(response.json_body, list)


@pytest.mark.usefixtures('default_data')
def test_api_describe(request_helper):
    """
    Test API describe action for root API resource.

    """
    response = request_helper.get_json('/time/api/v1/@describe')
    assert response.status == '200 OK'
    assert isinstance(response.json, dict)
    assert response.json.get('version') == 'v1'
    # Check that response contains a list of API resources
    assert 'resources' in response.json
    assert isinstance(response.json['resources'], list)
    assert len(response.json['resources'])
