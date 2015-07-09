import pytest

from pyramid.exceptions import NotFound

from sandglass.time.api.v1.user import UserResource

from fixtures import UserData

USER_DATA = [
    {
        'first_name': u"Dr. Jurij",
        'last_name': u"Schiwago",
        'email': u"omarsharif@wienfluss.net",
        'password': "1234",
    }, {
        'first_name': u"Richard",
        'last_name': u"Blaine",
        'email': u"humphreybogart@wienfluss.net",
        'password': "1234",
    }, {
        'first_name': u"Max",
        'last_name': u"Adler",
        'email': u"heldenintirol@wienfluss.net",
        'password': "1234",
    },
]


def test_user_create_single(request_helper, default_data):
    # Create a user
    url = UserResource.get_collection_path()
    data = USER_DATA[0]
    response = request_helper.post_json(url, [data])
    # All post to collection should returns a collection
    assert isinstance(response.json_body, list) is True
    # User updated information is returned a single item in a list
    user_data = response.json[0]
    created_id = user_data['id']

    # Get newly created user based on ID
    url = UserResource.get_member_path(created_id)
    response = request_helper.get_json(url)
    assert response.status == '200 OK'

    # Check that user data is right
    new_user = response.json
    assert new_user['first_name'] == data['first_name']
    assert new_user['last_name'] == data['last_name']
    assert new_user['email'] == data['email']


def test_user_update_single(request_helper, default_data, fixture):
    fixture.data(UserData).setup()

    # Get user data
    data = dict(USER_DATA[2])

    # Get a random user
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    user = response.json[index]
    assert user['first_name'] != data['first_name']
    assert user['last_name'] != data['last_name']
    assert user['email'] != data['email']

    # Update user data
    url = UserResource.get_member_path(user['id'])
    data['id'] = user['id']
    response = request_helper.put_json(url, data)
    assert response.status == '200 OK'

    # Check that data was updated
    updated_user = response.json
    assert updated_user['first_name'] == data['first_name']
    assert updated_user['last_name'] == data['last_name']
    assert updated_user['email'] == data['email']


def test_user_get(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get a random user
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    user = response.json[index - 1]

    # get user using primary key
    url = UserResource.get_member_path(user['id'])
    response = request_helper.get_json(url)
    assert response.status == '200 OK'

    # Check that user is the same for both cases
    same_user = response.json
    assert user['first_name'] == same_user['first_name']
    assert user['last_name'] == same_user['last_name']
    assert user['email'] == same_user['email']


def test_user_delete_single(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get a random user
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    user = response.json[index + 1]

    # Delete user using primary key
    url = UserResource.get_member_path(user['id'])
    response = request_helper.delete_json(url)
    assert response.status == '200 OK'

    # Check that user does not exist
    with pytest.raises(NotFound):
        request_helper.get_json(url)


def test_user_create_multiple(request_helper, default_data):
    # Check that only one exist
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    assert len(response.json) == 1

    # Create three users
    response = request_helper.post_json(url, USER_DATA)
    assert response.status == '200 OK'
    assert len(response.json) == 3

    # Only 4 users should exist
    response_get = request_helper.get_json(url)
    assert len(response_get.json) == 4


def test_user_update_multiple(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get two random users from database
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    index = len(response.json) / 2
    old_user_1 = response.json[index]
    old_user_2 = response.json[index + 1]

    # Use other users data to update old users
    new_user_1 = dict(USER_DATA[0])
    new_user_1['id'] = old_user_1['id']
    new_user_2 = dict(USER_DATA[1])
    new_user_2['id'] = old_user_2['id']

    data = [new_user_1, new_user_2]
    response = request_helper.put_json(url, data)
    assert response.status == '200 OK'
    # Check that 2 users were updated
    assert response.json_body['info']['count'] == 2

    url = UserResource.get_member_path(old_user_1['id'])
    user = request_helper.get_json(url).json
    assert user['first_name'] == new_user_1['first_name']
    assert user['last_name'] == new_user_1['last_name']
    assert user['email'] == new_user_1['email']

    url = UserResource.get_member_path(old_user_2['id'])
    user = request_helper.get_json(url).json
    assert user['first_name'] == new_user_2['first_name']
    assert user['last_name'] == new_user_2['last_name']
    assert user['email'] == new_user_2['email']


def test_user_signin(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    request_helper.require_authorization = False

    user = UserData.JamesWilliamElliot
    signin_data = {'email': user.email, 'password': user.password}
    # Signin using current user data
    url = UserResource.get_collection_path() + "@signin"
    response = request_helper.post_json(url, signin_data, expect_errors=True)
    assert response.status == '200 OK'

    assert 'token' in response.json
    assert 'key' in response.json
    assert response.json['token'] is not None
    assert response.json['key'] is not None


def test_user_signup(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    request_helper.require_authorization = False

    # Signup a user
    url = UserResource.get_collection_path() + "@signup"
    response = request_helper.post_json(url, USER_DATA[2])
    assert response.status == '200 OK'

    assert 'token' in response.json
    assert 'key' in response.json
    assert response.json['token'] is not None
    assert response.json['key'] is not None


def test_user_delete_multiple(request_helper, default_data, fixture):
    fixture.data(UserData).setup()

    # Get number of users
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    user_count = len(response.json)

    # Get two random users from database
    index = len(response.json) / 2
    old_user_1 = response.json[index]
    old_user_2 = response.json[index + 1]

    # Delete 2 users
    data = [old_user_1, old_user_2]
    response = request_helper.delete_json(url, data)
    assert response.status == '200 OK'
    assert response.json_body['info']['count'] == 2

    # Check that both users were deleted
    deleted_ids = [old_user_1['id'], old_user_2['id']]
    response = request_helper.get_json(url, params={'id': deleted_ids})
    assert response.status == '200 OK'
    # Check that no user was returned
    assert not response.json

    # Get number of users again
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    # Check that there are 2 users less
    assert (user_count - 2) == len(response.json)

    # Calls to delete without JSON data should fail
    response = request_helper.delete_json(url)
    assert response.status_int == 400
    assert 'error' in response.json
    assert response.json['error'].get('code') == 'INVALID_JSON_DATA'


def test_user_data_field(request_helper, default_data, fixture):
    """
    Test for user data (JSON) field.

    """
    data = fixture.data(UserData)
    data.setup()

    # Get the first user in list
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status_int == 200
    assert isinstance(response.json_body, list)
    user = response.json_body[0]

    # Update user data field
    user['data'] = {'test_field': 'test_value'}
    url = UserResource.get_member_path(user['id'])
    response = request_helper.put_json(url, user)
    assert response.status_int == 200
    assert isinstance(response.json_body, dict)

    # Check that user has the new data values
    user = response.json_body
    assert isinstance(user['data'], dict)
    assert 'test_field' in user['data']
    assert user['data']['test_field'] == 'test_value'
    assert len(user['data']) == 1
