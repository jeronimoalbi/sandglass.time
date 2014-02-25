from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests.fixtures import ClientData
from sandglass.time.api.v1.client import ClientResource
from sandglass.time.tests.api.v1.client_fixtures import ClientClientData
from sandglass.time.tests import fixture
from sandglass.time.tests import AuthData


class ClientResourceTest(FunctionalTestCase):

    """
    Functional tests for Client resource.

    """

    # Use authentication for each request by default
    require_authorization = True

    @fixture(AuthData)
    def test_create_single_client(self, data):
        client = ClientData.charles_magnussen
        url = ClientResource.get_collection_path()

        response = self.post_json(url, client.to_dict())
        created_id = response.json['id']

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

    @fixture(ClientData, AuthData)
    def test_update_single_user(self, data):
        # Get random user from DB
        url = ClientResource.get_collection_path()
        response = self.get_json(url)
        old_user = response.json[len(response.json) / 2]
        update_id = old_user['id']

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

        self.assertNotEqual(old_user['name'], new_client['name'])
