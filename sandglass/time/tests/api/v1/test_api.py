from sandglass.time.api.v1.user import UserResource
from sandglass.time.request import rest_collection_mode
from sandglass.time.tests import FunctionalTestCase
from sandglass.time.utils import get_settings


class ApiTest(FunctionalTestCase):
    """
    Functional tests for API generic functionality.

    """
    # Use authentication for each request by default
    require_authorization = True

    user_list = [
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

    def test_get_rest_collection_mode(self):
        """
        Check REST collection mode request property.

        """
        settings = get_settings()
        # Remove default value is is setted
        if 'request.rest_collection_mode' in settings:
            del settings['request.rest_collection_mode']

        # Check that mode is getted from request headers
        self.request.headers['X-REST-Collection-Mode'] = 'permissive'
        self.assertEqual(rest_collection_mode(self.request), 'permissive')
        self.request.headers['X-REST-Collection-Mode'] = 'strict'
        self.assertEqual(rest_collection_mode(self.request), 'strict')

        # Setting an invalid value should return a default value
        self.request.headers['X-REST-Collection-Mode'] = 'INVALID'
        # .. when no default exists in settings 'strict' is used as default
        self.assertEqual(rest_collection_mode(self.request), 'strict')
        # .. or if there is a default then it is used instead
        settings['request.rest_collection_mode'] = 'permissive'
        self.assertEqual(rest_collection_mode(self.request), 'permissive')

        # Finally remove setting to avoid messing with other tests
        del settings['request.rest_collection_mode']

    def test_strict_rest_collection_mode(self):
        headers = {'X-REST-Collection-Mode': 'strict'}
        user = self.user_list[0]
        url = UserResource.get_collection_path()

        # Mode strict should fail when no collection is sent
        response = self.post_json(url, user, headers=headers)
        self.assertEqual(response.status_int, 500)
        response_data = response.json_body
        self.assertTrue('error' in response_data)
        self.assertTrue('code' in response_data['error'])
        self.assertEqual(response_data['error']['code'], 'COLLECTION_EXPECTED')

        # When a collection is sent is should work and return a collection
        response = self.post_json(url, [user], headers=headers)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))

    def test_permissive_rest_collection_mode(self):
        headers = {'X-REST-Collection-Mode': 'permissive'}
        url = UserResource.get_collection_path()

        # Mode permissive should not fail when no collection is sent
        # and it should return an object when an object is sent
        user = self.user_list[0]
        response = self.post_json(url, user, headers=headers)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))

        # Mode permissive should return a list when a list is sent
        user = self.user_list[1]
        response = self.post_json(url, [user], headers=headers)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
