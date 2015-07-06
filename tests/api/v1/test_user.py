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


def test_create_single_user(request_helper, default_data):
    # Create first Test User
    url = UserResource.get_collection_path()

    data = USER_DATA[0]
    response = request_helper.post_json(url, [data])
    # All post to collection returns a collection
    assert isinstance(response.json_body, list) is True
    # User updated information is returned a single item in a list
    user_data = response.json[0]
    created_id = user_data['id']

    # Get newly created user based on ID
    url = UserResource.get_member_path(created_id)
    response = request_helper.get_json(url)

    # assert response is ok
    assert response.status == '200 OK'

    # Assert all data was written properly
    new_user = response.json
    assert new_user['first_name'] == data['first_name']
    assert new_user['last_name'] == data['last_name']
    assert new_user['email'] == data['email']

    # Cleanup - delete created user
    url = UserResource.get_member_path(created_id)
    response = request_helper.delete_json(url)
    # assert response is ok
    assert response.status == '200 OK'


def test_update_single_user(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get random user from DB
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    old_user = response.json[len(response.json) / 2]
    update_id = old_user['id']

    # Change it to Humphrey Bogart
    url = UserResource.get_member_path(update_id)
    data = dict(USER_DATA[2])
    data['id'] = update_id
    response = request_helper.put_json(url, data)

    # assert response is ok
    assert response.status == '200 OK'

    # Assert equal/different
    new_user = response.json
    assert new_user['first_name'] == data['first_name']
    assert new_user['last_name'] == data['last_name']
    assert new_user['email'] == data['email']

    assert old_user['first_name'] != new_user['first_name']
    assert old_user['last_name'] != new_user['last_name']
    assert old_user['email'] != new_user['email']


def test_get_user(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get random user from DB
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    old_user = response.json[(len(response.json) / 2) - 1]
    get_id = old_user['id']

    # Get that user again, this time via it's PK
    url = UserResource.get_member_path(get_id)
    response = request_helper.get_json(url)

    # assert response is ok
    assert response.status == '200 OK'

    get_user = response.json

    # Assert all is the same
    assert old_user['first_name'] == get_user['first_name']
    assert old_user['last_name'] == get_user['last_name']
    assert old_user['email'] == get_user['email']


def test_delete_single_user(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get random user from DB
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    old_user = response.json[(len(response.json) / 2) + 1]
    get_id = old_user['id']

    # Delete that user again, this time via it's PK
    url = UserResource.get_member_path(get_id)
    response = request_helper.delete_json(url)

    # assert it went ok
    assert response.status == '200 OK'

    # try getting it again, make sure it's gone
    with pytest.raises(NotFound):
        request_helper.get_json(url, status=404)


def test_create_multiple_users(request_helper, default_data):
    # Check that only the one testuser exist
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    assert len(response.json) == 1
    assert response.json[0]['first_name'] == 'Admin'
    assert response.json[0]['last_name'] == 'User'

    # Create three users at the same time
    response = request_helper.post_json(url, USER_DATA)

    # assert response is ok
    assert response.status == '200 OK'
    assert len(response.json) == 3

    # assert now only four users exist
    response_get = request_helper.get_json(url)
    assert len(response_get.json) == 4

    # Cleanup the custom created users
    for user in response.json:
        url = UserResource.get_member_path(user['id'])

        response_delete = request_helper.delete_json(url)
        # assert it went ok
        assert response_delete.status == '200 OK'


def test_update_multiple_users(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get two random users from DB
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    old_user_1 = response.json[(len(response.json) / 2)]
    old_user_2 = response.json[(len(response.json) / 2) + 1]
    update_ids = [old_user_1['id'], old_user_2['id']]

    # Change them to Humphrey Bogart and Max Adler
    #url = UserResource.get_member_path(update_id)
    new_user_1 = dict(USER_DATA[0])
    new_user_2 = dict(USER_DATA[1])
    data = [new_user_1, new_user_2]
    data[0]['id'] = update_ids[0]
    data[1]['id'] = update_ids[1]
    response = request_helper.put_json(url, data)

    # assert response is ok
    assert response.status == '200 OK'

    # Assert two were updated
    assert response.json_body['info']['count'] == 2

    url = UserResource.get_member_path(update_ids[0])
    response_user = request_helper.get_json(url).json

    assert response_user['first_name'] == new_user_1['first_name']
    assert response_user['last_name'] == new_user_1['last_name']
    assert response_user['email'] == new_user_1['email']

    url = UserResource.get_member_path(update_ids[1])
    response_user = request_helper.get_json(url).json
    assert response_user['first_name'] == new_user_2['first_name']
    assert response_user['last_name'] == new_user_2['last_name']
    assert response_user['email'] == new_user_2['email']


def test_signin(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    request_helper.require_authorization = False

    user = UserData.JamesWilliamElliot
    signin_data = {'email': user.email, 'password': user.password}

    # Try and log in with the testuser
    url = UserResource.get_collection_path() + "@signin"
    response = request_helper.post_json(url, signin_data, expect_errors=True)

    # assert response is ok
    assert response.status == '200 OK'

    assert 'token' in response.json
    assert 'key' in response.json

    assert response.json['token'] is not None
    assert response.json['key'] is not None

    request_helper.require_authorization = True


def test_signup(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    request_helper.require_authorization = False

    # Try and sign up with the testuser
    url = UserResource.get_collection_path() + "@signup"
    response = request_helper.post_json(url, USER_DATA[2])

    # assert response is ok
    assert response.status == '200 OK'

    assert 'token' in response.json
    assert 'key' in response.json

    assert response.json['token'] is not None
    assert response.json['key'] is not None

    request_helper.require_authorization = True


def test_delete_multiple_users(request_helper, default_data, fixture):
    data = fixture.data(UserData)
    data.setup()

    # Get two random users from DB
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    old_user_1 = response.json[(len(response.json) / 2)]
    old_user_2 = response.json[(len(response.json) / 2) + 1]
    data = [old_user_1, old_user_2]
    delete_ids = [old_user_1['id'], old_user_2['id']]

    response = request_helper.delete_json(url, data)

    # assert response is ok
    assert response.status == '200 OK'
    assert response.json_body['info']['count'] == 2

    # assert they are actually deleted
    # try getting it again, make sure it's gone
    with pytest.raises(NotFound):
        for pk_value in delete_ids:
            url = UserResource.get_member_path(pk_value)
            request_helper.get_json(url, status=404)

    # Get amount of users left in DB
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)

    response = request_helper.delete_json(url, expect_errors=True)
    # assert response is error
    assert response.status_int == 400


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
