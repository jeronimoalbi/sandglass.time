import pytest

from pyramid.exceptions import NotFound

from sandglass.time.api.v1.client import ClientResource

from fixtures import ClientData

CLIENT_DATA = [
    {
        'name': 'Irene Adler',
    }, {
        'name': 'Violet Hunter',
    },
]


def test_client_create_single(request_helper, default_data):
    url = ClientResource.get_collection_path()
    data = CLIENT_DATA[0]
    response = request_helper.post_json(url, [data])
    assert response.status == '200 OK'
    # All post to collection should returns a collection
    assert isinstance(response.json_body, list)
    # User updated information is returned a single item in a list
    client_data = response.json[0]
    created_id = client_data['id']

    # Get newly created user based on ID
    url = ClientResource.get_member_path(created_id)
    response = request_helper.get_json(url)
    assert response.status == '200 OK'

    # Check that client data is right
    new_client = response.json
    assert new_client['name'] == data['name']


def test_client_update_single(request_helper, default_data, fixture):
    fixture.data(ClientData).setup()

    # Get a random client
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    old_client = response.json[index]

    # Update client
    url = ClientResource.get_member_path(old_client['id'])
    data = dict(CLIENT_DATA[0])
    data['id'] = old_client['id']
    response = request_helper.put_json(url, data)
    assert response.status == '200 OK'

    # Check that data was updated
    new_client = response.json
    assert new_client['name'] == data['name']
    assert old_client['name'] != new_client['name']


def test_client_get(request_helper, default_data, fixture):
    fixture.data(ClientData).setup()

    # Get random client
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    client = response.json[index - 1]

    # Check that client is the same for both cases
    url = ClientResource.get_member_path(client['id'])
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    same_client = response.json
    assert client['name'] == same_client['name']


def test_client_delete_single(request_helper, default_data, fixture):
    fixture.data(ClientData).setup()

    # Get random user from DB
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    client = response.json[index + 1]

    # Delete that user again, this time via it's PK
    url = ClientResource.get_member_path(client['id'])
    response = request_helper.delete_json(url)
    assert response.status == '200 OK'

    # try getting it again, make sure it's gone
    with pytest.raises(NotFound):
        request_helper.get_json(url)


def test_client_create_multiple(request_helper, default_data):
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    assert len(response.json) == 0

    # Create three clients
    response = request_helper.post_json(url, CLIENT_DATA)
    assert response.status == '200 OK'
    assert len(response.json) == len(CLIENT_DATA)

    # Only 3 more clients should exist
    response_get = request_helper.get_json(url)
    assert len(response_get.json) == len(CLIENT_DATA)


def test_client_update_multiple(request_helper, default_data, fixture):
    fixture.data(ClientData).setup()

    # Get two random users from DB
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    old_client_1 = response.json[index]
    old_client_2 = response.json[index + 1]

    # Change them to Humphrey Bogart and Max Adler
    new_client_1 = dict(CLIENT_DATA[0])
    new_client_1['id'] = old_client_1['id']
    new_client_2 = dict(CLIENT_DATA[1])
    new_client_2['id'] = old_client_2['id']
    data = [new_client_1, new_client_2]
    response = request_helper.put_json(url, data)
    assert response.status == '200 OK'
    # Check that 2 were updated
    assert response.json_body['info']['count'] == 2

    url = ClientResource.get_member_path(old_client_1['id'])
    response_client = request_helper.get_json(url).json
    assert response_client['name'] == new_client_1['name']

    url = ClientResource.get_member_path(old_client_2['id'])
    response_client = request_helper.get_json(url).json
    assert response_client['name'] == new_client_2['name']


def test_client_delete_multiple(request_helper, default_data, fixture):
    fixture.data(ClientData).setup()

    # Get number of clients
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    client_count = len(response.json)

    # Get two random clients
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    old_client_1 = response.json[index]
    old_client_2 = response.json[index + 1]

    # Delete 2 clients
    data = [old_client_1, old_client_2]
    response = request_helper.delete_json(url, data)
    assert response.status == '200 OK'
    assert response.json_body['info']['count'] == 2

    # Check that both clients were deleted
    deleted_ids = [old_client_1['id'], old_client_2['id']]
    response = request_helper.get_json(url, params={'id': deleted_ids})
    assert response.status == '200 OK'
    # Check that no client was returned
    assert not response.json

    # Get number of clients again
    url = ClientResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    # Check that there are 2 clients less
    assert (client_count - 2) == len(response.json)

    # Calls to delete without JSON data should fail
    response = request_helper.delete_json(url)
    assert response.status_int == 400
    assert 'error' in response.json
    assert response.json['error'].get('code') == 'INVALID_JSON_DATA'
