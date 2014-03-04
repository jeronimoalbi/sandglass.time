from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests.fixtures import ClientData
from sandglass.time.api.v1.client import ClientResource
from sandglass.time.tests.api.v1.client_fixtures import ClientClientData
from sandglass.time.tests import fixture

from pyramid.exceptions import NotFound


class ClientResourceTest(FunctionalTestCase):
    """
    Functional tests for Client resource.

    """

    # Use authentication for each request by default
    require_authorization = True

    def test_client_create_single(self):
        client = ClientData.charles_magnussen
        url = ClientResource.get_collection_path()

        response = self.post_json(url, [client.to_dict()])
        # All post to collection returns a collection
        self.assertTrue(isinstance(response.json_body, list))
        # User updated information is returned a single item in a list
        client_data = response.json[0]
        created_id = client_data['id']

        # Asserts
        self.assertEqual(response.status, '200 OK')

        # Get newly created user based on ID
        url = ClientResource.get_member_path(created_id)
        response = self.get_json(url)

        # Asserts
        self.assertEqual(response.status, '200 OK')

        new_client = response.json
        self.assertEqual(new_client['name'], client.name)

        # Cleanup - delete created user
        response = self.delete_json(url)
        # assert response is ok
        self.assertEqual(response.status, '200 OK')

    @fixture(ClientData)
    def test_client_update_single(self):
        # Get random user from DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        old_client = response.json[len(response.json) / 2]
        update_id = old_client['id']

        # Change it to Humphrey Bogart
        url = ClientResource.get_member_path(update_id)
        client = ClientClientData.irene_adler
        data = client.to_dict()
        data['id'] = update_id
        response = self.put_json(url, data)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        # Assert equal/different
        new_client = response.json
        self.assertEqual(new_client['name'], client.name)

        self.assertNotEqual(old_client['name'], new_client['name'])

    @fixture(ClientData)
    def test_client_get(self):
        # Get random user from DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        old_client = response.json[(len(response.json) / 2) - 1]
        get_id = old_client['id']

        # Get that user again, this time via it's PK
        url = ClientResource.get_member_path(get_id)
        response = self.get_json(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        get_client = response.json

        # Assert all is the same
        self.assertEqual(old_client['name'], get_client['name'])

    @fixture(ClientData)
    def test_client_delete_single(self):
        # Get random user from DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        old_client = response.json[(len(response.json) / 2) + 1]
        get_id = old_client['id']

        # Delete that user again, this time via it's PK
        url = ClientResource.get_member_path(get_id)
        response = self.delete_json(url)

        # assert it went ok
        self.assertEqual(response.status, '200 OK')

        # try getting it again, make sure it's gone
        with self.assertRaises(NotFound):
            self.get_json(url, status=404)

    def test_client_create_multiple(self):
        # Check that only the one testuser exist
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        self.assertEqual(len(response.json), 0)

        # Create three clients at the same time
        clients = [ClientData.charles_magnussen.to_dict(),
                   ClientData.greg_lestrade.to_dict(),
                   ClientData.john_watson.to_dict()]

        response = self.post_json(url, clients)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(len(response.json), 3)

        # assert now only four clients exist
        response_get = self.get_json(url)
        self.assertEqual(len(response_get.json), 3)

        # Cleanup the custom created clients
        for client in response.json:
            url = ClientResource.get_member_path(client['id'])

            response_delete = self.delete_json(url)
            # assert it went ok
            self.assertEqual(response_delete.status, '200 OK')

    @fixture(ClientData)
    def test_update_multiple_users(self):
        # Get two random users from DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        old_client_1 = response.json[(len(response.json) / 2)]
        old_client_2 = response.json[(len(response.json) / 2) + 1]
        update_ids = [old_client_1['id'], old_client_2['id']]

        # Change them to Humphrey Bogart and Max Adler
        new_client_1 = ClientClientData.irene_adler
        new_client_2 = ClientClientData.violet_hunter
        data = [new_client_1.to_dict(), new_client_2.to_dict()]
        data[0]['id'] = update_ids[0]
        data[1]['id'] = update_ids[1]
        response = self.put_json(url, data)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        # Assert two were updated
        self.assertEqual(response.json_body['info']['count'], 2)

        url = ClientResource.get_member_path(update_ids[0])
        response_client = self.get_json(url).json

        self.assertEqual(response_client['name'], new_client_1.name)

        url = ClientResource.get_member_path(update_ids[1])
        response_client = self.get_json(url).json
        self.assertEqual(response_client['name'], new_client_2.name)

    @fixture(ClientData)
    def test_client_delete_multiple(self):

        # Get two random users from DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        old_client_1 = response.json[(len(response.json) / 2)]
        old_client_2 = response.json[(len(response.json) / 2) + 1]
        data = [old_client_1, old_client_2]
        delete_ids = [old_client_1['id'], old_client_2['id']]

        response = self.delete_json(url, data)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json_body['info']['count'], 2)

        # assert they are actually deleted
        # try getting it again, make sure it's gone
        with self.assertRaises(NotFound):
            for pk_value in delete_ids:
                url = ClientResource.get_member_path(pk_value)
                self.get_json(url, status=404)

        # Get amount of users left in DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)

        response = self.delete_json(url, expect_errors=True)
        # assert response is error
        self.assertEqual(response.status_int, 500)
