from pyramid.exceptions import NotFound

from sandglass.time.api.v1.user import UserResource
from sandglass.time.tests import fixture
from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests.api.v1.client_fixtures import ClientUserData
from sandglass.time.tests.fixtures import UserData


class UserResourceTest(FunctionalTestCase):
    """
    Functional tests for User resource.

    """

    # Use authentication for each request by default
    require_authorization = True

    def test_create_single_user(self):
        # Create first Test User
        user = ClientUserData.dr_schiwago
        url = UserResource.get_collection_path()

        response = self.post_json(url, [user.to_dict()])
        # All post to collection returns a collection
        self.assertTrue(isinstance(response.json_body, list))
        # User updated information is returned a single item in a list
        user_data = response.json[0]
        created_id = user_data['id']

        # Get newly created user based on ID
        url = UserResource.get_member_path(created_id)
        response = self.get_json(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        # Assert all data was written properly
        new_user = response.json
        self.assertEqual(new_user['first_name'], user.first_name)
        self.assertEqual(new_user['last_name'], user.last_name)
        self.assertEqual(new_user['email'], user.email)

        # Cleanup - delete created user
        url = UserResource.get_member_path(created_id)
        response = self.delete_json(url)
        # assert response is ok
        self.assertEqual(response.status, '200 OK')

    @fixture(UserData)
    def test_update_single_user(self):
        # Get random user from DB
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        old_user = response.json[len(response.json) / 2]
        update_id = old_user['id']

        # Change it to Humphrey Bogart
        url = UserResource.get_member_path(update_id)
        user = ClientUserData.humphrey_bogart
        data = user.to_dict()
        data['id'] = update_id
        response = self.put_json(url, data)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        # Assert equal/different
        new_user = response.json
        self.assertEqual(new_user['first_name'], user.first_name)
        self.assertEqual(new_user['last_name'], user.last_name)
        self.assertEqual(new_user['email'], user.email)

        self.assertNotEqual(old_user['first_name'], new_user['first_name'])
        self.assertNotEqual(old_user['last_name'], new_user['last_name'])
        self.assertNotEqual(old_user['email'], new_user['email'])

    @fixture(UserData)
    def test_get_user(self):
        # Get random user from DB
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        old_user = response.json[(len(response.json) / 2) - 1]
        get_id = old_user['id']

        # Get that user again, this time via it's PK
        url = UserResource.get_member_path(get_id)
        response = self.get_json(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        get_user = response.json

        # Assert all is the same
        self.assertEqual(old_user['first_name'], get_user['first_name'])
        self.assertEqual(old_user['last_name'], get_user['last_name'])
        self.assertEqual(old_user['email'], get_user['email'])

    @fixture(UserData)
    def test_delete_single_user(self):
        # Get random user from DB
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        old_user = response.json[(len(response.json) / 2) + 1]
        get_id = old_user['id']

        # Delete that user again, this time via it's PK
        url = UserResource.get_member_path(get_id)
        response = self.delete_json(url)

        # assert it went ok
        self.assertEqual(response.status, '200 OK')

        # try getting it again, make sure it's gone
        with self.assertRaises(NotFound):
            self.get_json(url, status=404)

    def test_create_multiple_users(self):
        # Check that only the one testuser exist
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['first_name'], 'Admin')
        self.assertEqual(response.json[0]['last_name'], 'User')

        # Create three users at the same time
        users = [ClientUserData.dr_schiwago.to_dict(),
                 ClientUserData.max_adler.to_dict(),
                 ClientUserData.humphrey_bogart.to_dict()]

        response = self.post_json(url, users)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json), 3)

        # assert now only four users exist
        response_get = self.get_json(url)
        self.assertEqual(len(response_get.json), 4)

        # Cleanup the custom created users
        for user in response.json:
            url = UserResource.get_member_path(user['id'])

            response_delete = self.delete_json(url)
            # assert it went ok
            self.assertEqual(response_delete.status, '200 OK')

    @fixture(UserData)
    def test_update_multiple_users(self):
        # Get two random users from DB
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        old_user_1 = response.json[(len(response.json) / 2)]
        old_user_2 = response.json[(len(response.json) / 2) + 1]
        update_ids = [old_user_1['id'], old_user_2['id']]

        # Change them to Humphrey Bogart and Max Adler
        #url = UserResource.get_member_path(update_id)
        new_user_1 = ClientUserData.humphrey_bogart
        new_user_2 = ClientUserData.max_adler
        data = [new_user_1.to_dict(), new_user_2.to_dict()]
        data[0]['id'] = update_ids[0]
        data[1]['id'] = update_ids[1]
        response = self.put_json(url, data)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        # Assert two were updated
        self.assertEqual(response.json_body['info']['count'], 2)

        url = UserResource.get_member_path(update_ids[0])
        response_user = self.get_json(url).json

        self.assertEqual(response_user['first_name'], new_user_1.first_name)
        self.assertEqual(response_user['last_name'], new_user_1.last_name)
        self.assertEqual(response_user['email'], new_user_1.email)

        url = UserResource.get_member_path(update_ids[1])
        response_user = self.get_json(url).json
        self.assertEqual(response_user['first_name'], new_user_2.first_name)
        self.assertEqual(response_user['last_name'], new_user_2.last_name)
        self.assertEqual(response_user['email'], new_user_2.email)

    @fixture(UserData)
    def test_sign_in(self):
        self.require_authorization = False

        user = UserData.james_william_elliot

        # Try and log in with the testuser
        url = UserResource.get_collection_path() + "@signin"
        response = self.post_json(url, user.to_dict(), expect_errors=True)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        self.assertTrue('token' in response.json)
        self.assertTrue('key' in response.json)

        self.assertIsNotNone(response.json['token'])
        self.assertIsNotNone(response.json['key'])

        self.require_authorization = True

    @fixture(UserData)
    def test_sign_up(self):
        self.require_authorization = False

        user = ClientUserData.max_adler

        # Try and sign up with the testuser
        url = UserResource.get_collection_path() + "@signup"
        response = self.post_json(url, user.to_dict())

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        self.assertTrue('token' in response.json)
        self.assertTrue('key' in response.json)

        self.assertIsNotNone(response.json['token'])
        self.assertIsNotNone(response.json['key'])

        self.require_authorization = True

    @fixture(UserData)
    def test_delete_multiple_users(self):
        # Get two random users from DB
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        old_user_1 = response.json[(len(response.json) / 2)]
        old_user_2 = response.json[(len(response.json) / 2) + 1]
        data = [old_user_1, old_user_2]
        delete_ids = [old_user_1['id'], old_user_2['id']]

        response = self.delete_json(url, data)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json_body['info']['count'], 2)

        # assert they are actually deleted
        # try getting it again, make sure it's gone
        with self.assertRaises(NotFound):
            for pk_value in delete_ids:
                url = UserResource.get_member_path(pk_value)
                self.get_json(url, status=404)

        # Get amount of users left in DB
        url = UserResource.get_collection_path()
        response = self.get_json(url)

        response = self.delete_json(url, expect_errors=True)
        # assert response is error
        self.assertEqual(response.status_int, 500)

    @fixture(UserData)
    def test_user_data_field(self):
        """
        Test for user data (JSON) field.

        """
        # Get the first user in list
        url = UserResource.get_collection_path()
        response = self.get_json(url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        user = response.json_body[0]

        # Update user data field
        user['data'] = {'test_field': 'test_value'}
        url = UserResource.get_member_path(user['id'])
        response = self.put_json(url, user)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))

        # Check that user has the new data values
        user = response.json_body
        self.assertTrue(isinstance(user['data'], dict))
        self.assertTrue('test_field' in user['data'])
        self.assertEqual(user['data']['test_field'], 'test_value')
        self.assertEqual(len(user['data']), 1)
