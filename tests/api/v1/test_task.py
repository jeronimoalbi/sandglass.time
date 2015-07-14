import pytest

from pyramid.exceptions import NotFound

from sandglass.time.api.v1.task import TaskResource

TASK_DATA = [
    {
        'name': 'Task 1',
    },
]


def test_task_create_single(request_helper, default_data, session):
    """
    Create a single task using the API.

    """
    user = default_data.users.dr_who
    session.add(user)
    project = default_data.projects.public_project
    session.add(project)

    task_data = {
        'name': u"Test task",
        'user_id': user.id,
        'project_id': project.id,
    }
    url = TaskResource.get_collection_path()
    # Create the new task
    response = request_helper.post_json(url, [task_data])
    # Check for success, and that body contains a list with one element
    assert response.status_int == 200
    assert isinstance(response.json_body, list)
    assert len(response.json_body) == 1
    # Check that task has a valid ID value
    task = response.json_body[0]
    assert 'id' in task
    assert isinstance(task['id'], int)


@pytest.mark.usefixtures('default_data')
def test_task_update_single(request_helper):
    """
    Update a single task using the API.

    """
    task_data = dict(TASK_DATA[0])
    # Get a task
    url = TaskResource.get_collection_path()
    response = request_helper.get_json(url)
    task = response.json[0]
    assert task['name'] != task_data['name']

    # Update data
    url = TaskResource.get_member_path(task['id'])
    task_data['id'] = task['id']
    # Try to update without a required field
    response = request_helper.put_json(url, task_data)
    assert response.status == '400 Bad Request'
    assert 'error' in response.json
    assert response.json['error']['code'] == 'VALIDATION_ERROR'
    assert 'user_id' in response.json['error']['fields']

    # Update should work now
    task_data['user_id'] = task['user_id']
    response = request_helper.put_json(url, task_data)
    assert response.status == '200 OK'
    # Check that data was updated
    updated_data = response.json
    assert updated_data['name'] == task_data['name']


@pytest.mark.usefixtures('default_data')
def test_task_delete_single(request_helper):
    """
    Delete a single task using the API.

    """
    # Get a task
    url = TaskResource.get_collection_path()
    response = request_helper.get_json(url)
    task = response.json[0]

    # Delete it using primary key
    url = TaskResource.get_member_path(task['id'])
    response = request_helper.delete_json(url)
    assert response.status == '200 OK'

    # Check that it does not exist anymore
    with pytest.raises(NotFound):
        request_helper.get_json(url)


def test_task_with_project(request_helper, default_data, session):
    """
    Test a task with a projects.

    """
    task = default_data.tasks.backend
    session.add(task)
    session.add(task.project)

    url = TaskResource.get_related_path(task.id, 'project')
    # Get task project data
    response = request_helper.get_json(url)
    assert response.status_int == 200
    assert isinstance(response.json_body, dict)

    # Check that project is the same as the requested task data
    project = response.json_body
    assert task.project.id == project['id']
