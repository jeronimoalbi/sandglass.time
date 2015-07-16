from datetime import datetime

import pytest

from pyramid.exceptions import NotFound
from pyramid.httpexceptions import HTTPNotFound

from sandglass.time.api.v1.activity import ActivityResource
from sandglass.time.api.v1.user import UserResource

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


@pytest.mark.usefixtures('default_data')
def test_user_create_single(request_helper):
    # Create a user
    url = UserResource.get_collection_path()
    data = USER_DATA[0]
    response = request_helper.post_json(url, [data])
    # All post to collection should returns a collection
    assert isinstance(response.json, list) is True
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


@pytest.mark.usefixtures('default_data')
def test_user_update_single(request_helper):
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


@pytest.mark.usefixtures('default_data')
def test_user_get(request_helper):
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


@pytest.mark.usefixtures('default_data')
def test_user_delete_single(request_helper):
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


@pytest.mark.usefixtures('default_data')
def test_user_create_multiple(request_helper):
    # Check that only one exist
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    user_count = len(response.json)
    assert user_count > 0

    # Create three users
    response = request_helper.post_json(url, USER_DATA)
    assert response.status == '200 OK'
    assert len(response.json) == len(USER_DATA)

    # Only 4 more users should exist
    response_get = request_helper.get_json(url)
    assert len(response_get.json) == len(USER_DATA) + user_count


@pytest.mark.usefixtures('default_data')
def test_user_update_multiple(request_helper):
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
    assert response.json['info']['count'] == 2

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


def test_user_signin(request_helper, default_data, session):
    request_helper.require_authorization = False

    user = default_data.users.james_william_elliot
    session.add(user)

    signin_data = {'email': user.email, 'password': 'test'}

    # Signin using current user data
    url = UserResource.get_collection_path() + "@signin"
    response = request_helper.post_json(url, signin_data, expect_errors=True)
    assert response.status == '200 OK'
    assert 'token' in response.json
    assert 'key' in response.json
    assert response.json['token'] is not None
    assert response.json['key'] is not None

    # Try to signin using an invalid password
    signin_data['password'] = 'invalid'
    response = request_helper.post_json(url, signin_data, expect_errors=True)
    assert response.status == '400 Bad Request'
    assert isinstance(response.json, dict)
    assert 'error' in response.json
    assert response.json['error']['code'] == 'INVALID_SIGNIN'


@pytest.mark.usefixtures('default_data')
def test_user_signup(request_helper):
    request_helper.require_authorization = False

    # Signup a user
    url = UserResource.get_collection_path() + "@signup"
    response = request_helper.post_json(url, USER_DATA[2])
    assert response.status == '200 OK'
    assert isinstance(response.json, dict)
    assert 'token' in response.json
    assert 'key' in response.json
    assert response.json['token'] is not None
    assert response.json['key'] is not None

    # Signin an existing user
    response = request_helper.post_json(url, USER_DATA[2])
    assert response.status == '400 Bad Request'
    assert isinstance(response.json, dict)
    assert 'error' in response.json
    assert response.json['error']['code'] == 'USER_EMAIL_EXISTS'


@pytest.mark.usefixtures('default_data')
def test_user_delete_multiple(request_helper):
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
    assert response.json['info']['count'] == 2

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
    assert response.json['error'].get('code') == 'COLLECTION_EXPECTED'


@pytest.mark.usefixtures('default_data')
def test_user_data_field(request_helper):
    """
    Test for user data (JSON) field.

    """
    # Get the first user in list
    url = UserResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    user = response.json[0]

    # Update user data field
    user['data'] = {'test_field': 'test_value'}
    url = UserResource.get_member_path(user['id'])
    response = request_helper.put_json(url, user)
    assert response.status_int == 200
    assert isinstance(response.json, dict)

    # Check that user has the new data values
    user = response.json
    assert isinstance(user['data'], dict)
    assert 'test_field' in user['data']
    assert user['data']['test_field'] == 'test_value'
    assert len(user['data']) == 1


def test_user_search(request_helper, default_data, session):
    user = default_data.users.dr_who
    session.add(user)

    url = UserResource.get_collection_path() + '@search'
    # Search user by email
    response = request_helper.get_json(url, params={'email': user.email})
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'id' in response.json
    assert response.json['id'] == user.id

    # Search user by token
    response = request_helper.get_json(url, params={'token': user.token})
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'id' in response.json
    assert response.json['id'] == user.id

    # Search user using invalid an invalid value
    response = request_helper.get_json(url, params={'token': 'INVALID'})
    assert response.status == '400 Bad Request'
    assert isinstance(response.json, dict)
    assert 'error' in response.json
    assert response.json['error']['code'] == 'USER_NOT_FOUND'


def test_user_activities(request_helper, default_data, session):
    project = default_data.projects.public_project
    task = default_data.tasks.backend
    # TODO: Use this user to authenticate requests instead of admin
    user = default_data.users.dr_who
    session.add_all([project, task, user])

    today = datetime.today()
    (year, month, day) = (today.year, today.month, today.day)

    # Create new activities for current user
    activity_data = [
        {
            'description': u"Test activity",
            'project_id': project.id,
            'task_id': task.id,
            'user_id': user.id,
            'start': datetime(year, month, day, 8, 0).isoformat(),
            'end': datetime(year, month, day, 8, 30).isoformat(),
        }, {
            'description': u"Test activity 2",
            'project_id': project.id,
            'task_id': task.id,
            'user_id': user.id,
            'start': datetime(year, month, day, 9, 0).isoformat(),
            'end': datetime(year, month, day, 9, 30).isoformat(),
        }
    ]

    activities_url = ActivityResource.get_collection_path()
    response = request_helper.post_json(activities_url, activity_data)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == len(activity_data)

    # Get the IDs for the new activities
    activities_id_list = [activity['id'] for activity in response.json]
    activities_id_list.sort()

    # Get today activities for current user
    user_activities_url = UserResource.get_member_path(user.id) + '@activities'
    response = request_helper.get_json(user_activities_url)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == len(activity_data)
    user_activities_id_list = [activity['id'] for activity in response.json]
    user_activities_id_list.sort()
    # Check that response gave all user activities
    assert user_activities_id_list == activities_id_list

    # Get today activities for current user until 8:40hs
    params = {
        'to': datetime(year, month, day, 8, 40).isoformat(),
    }
    response = request_helper.get_json(user_activities_url, params=params)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == 1

    # Get today activities for current user from 8:40hs
    params = {
        'from': datetime(year, month, day, 8, 40).isoformat(),
    }
    response = request_helper.get_json(user_activities_url, params=params)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == 1

    # Get today activities for current user from 7:00hs until 8:40hs
    params = {
        'from': datetime(year, month, day, 7, 0).isoformat(),
        'to': datetime(year, month, day, 8, 40).isoformat(),
    }
    response = request_helper.get_json(user_activities_url, params=params)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert len(response.json) == 1

    # Use an invalid date to get activities.
    params = {'to': 'INVALID DATE'}
    response = request_helper.get_json(user_activities_url, params=params)
    assert response.status == '400 Bad Request'
    assert isinstance(response.json, dict)
    assert response.json.get('error')

    # Use an invalid user to get activities
    url = UserResource.get_member_path(9999) + '@activities'
    with pytest.raises(HTTPNotFound):
        response = request_helper.get_json(url)
