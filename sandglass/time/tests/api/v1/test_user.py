from sandglass.time.api.v1.user import UserResource
from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests.fixtures import UserData, ClientData, ProjectData
from client_fixtures import ClientUserData
from sandglass.time.tests import fixture
import unittest
from pyramid.exceptions import NotFound


class UserResourceTest(FunctionalTestCase):

    """
    Functional tests for User resource.

    """

    def setUp(self):
        super(UserResourceTest, self).setUp()

    def tearDown(self):
        super(UserResourceTest, self).tearDown()
        self.clear_database()

    @fixture(UserData)
    def test_create_single_user(data, self):
        # Create first Test User
        user = ClientUserData.dr_schiwago
        url = UserResource.get_collection_path()
        response = self.app.post_json(url, [user.data()])
        created_id = response.json[0]['id']

        # Get newly created user based on ID
        url = UserResource.get_member_path(created_id)
        response = self.app.get(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        # Assert all data was written properly
        new_user = response.json
        self.assertEqual(new_user['first_name'], user.first_name)
        self.assertEqual(new_user['last_name'], user.last_name)
        self.assertEqual(new_user['email'], user.email)


    @fixture(UserData)
    def test_update_single_user(data, self):
        # Get random user from DB
        url = UserResource.get_collection_path()
        response = self.app.get(url)
        old_user = response.json[len(response.json) / 2]
        update_id = old_user['id']

        # Change it to Humphrey Bogart
        url = UserResource.get_member_path(update_id)
        user = ClientUserData.humphrey_bogart
        data = user.data()
        data['id'] = update_id
        response = self.app.put_json(url, data)

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
    def test_get_user(data, self):
        # Get random user from DB
        url = UserResource.get_collection_path()
        response = self.app.get(url)
        old_user = response.json[(len(response.json) / 2) - 1]
        get_id = old_user['id']

        # Get that user again, this time via it's PK
        url = UserResource.get_member_path(get_id)
        response = self.app.get(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        get_user = response.json

        # Assert all is the same
        self.assertEqual(old_user['first_name'], get_user['first_name'])
        self.assertEqual(old_user['last_name'], get_user['last_name'])
        self.assertEqual(old_user['email'], get_user['email'])

    @fixture(UserData)
    def test_delete_single_user(data, self):
        # Get random user from DB
        url = UserResource.get_collection_path()
        response = self.app.get(url)
        old_user = response.json[(len(response.json) / 2) + 1]
        get_id = old_user['id']

        # Delete that user again, this time via it's PK
        url = UserResource.get_member_path(get_id)
        response = self.app.delete_json(url)

        # assert it went ok
        self.assertEqual(response.status, '200 OK')

        # try getting it again, make sure it's gone
        with self.assertRaises(NotFound):
            self.app.get(url, status=404)

    def test_create_multiple_users(self):
        # Check that no users exist
        url = UserResource.get_collection_path()
        response = self.app.get(url)
        self.assertEqual(len(response.json), 0)

        # Create three users at the same time
        users = [ClientUserData.dr_schiwago.data(),
                ClientUserData.max_adler.data(),
                ClientUserData.humphrey_bogart.data()]

        response = self.app.post_json(url, users)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json), 3)
        

        # assert now only three users exist
        response = self.app.get(url)
        self.assertEqual(len(response.json), 3)


    @unittest.skip("showing class skipping")
    def test_update_multiple_users(self):
        self.fail()

    @unittest.skip("showing class skipping")
    def test_get_user_by_credentials(self):
        self.fail()

    @unittest.skip("showing class skipping")
    def test_delete_multiple_users(self):
        self.fail()
