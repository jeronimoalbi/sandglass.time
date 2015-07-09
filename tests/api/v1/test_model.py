from sandglass.time.api.v1.group import GroupResource
from sandglass.time.api.v1.project import ProjectResource

from fixtures import ProjectData

TESTS_DATA = {
    'groups': [
        {'name': u"Test Group 1", 'description': u"Test Group 1"},
        {'name': u"Test Group 2", 'description': u"Test Group 2"},
    ],
}


def test_delete_related_invalid_type(request_helper, default_data, fixture):
    """
    Check that an error is returned when deleting related with
    wrong request content type.

    """
    fixture.data(ProjectData).setup()

    project = ProjectData.PublicProject
    # Try to delete a group using an integer
    groups_url = ProjectResource.get_related_path(project.id, 'groups')
    response = request_helper.delete_json(groups_url, 1)
    assert response.status_int == 400
    assert isinstance(response.json, dict)
    # An error with VALIDATION_ERROR houls be returned
    assert 'error' in response.json
    error = response.json['error']
    assert error['code'] == 'VALIDATION_ERROR'


def test_put_related_invalid_type(request_helper, default_data, fixture):
    """
    Check that an error is returned when appending related with
    wrong request content type.

    """
    fixture.data(ProjectData).setup()

    project = ProjectData.PublicProject
    # Try to delete a group using an integer
    groups_url = ProjectResource.get_related_path(project.id, 'groups')
    response = request_helper.put_json(groups_url, 1)
    assert response.status_int == 400
    assert isinstance(response.json, dict)
    # An error with VALIDATION_ERROR houls be returned
    assert 'error' in response.json
    error = response.json['error']
    assert error['code'] == 'VALIDATION_ERROR'


def test_put_related_by_ids(request_helper, default_data, fixture):
    """
    Test appending to a collection of related objects by submitting IDs.

    """
    fixture.data(ProjectData).setup()

    project = ProjectData.PublicProject

    # Get groups for current project
    groups_url = ProjectResource.get_related_path(project.id, 'groups')
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    group_id_list = [group['id'] for group in response.json]
    assert len(group_id_list) == 3

    # Remove all related objects
    response = request_helper.delete_json(groups_url, group_id_list)
    assert response.status_int == 200
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 0

    # Append a single group by ID
    append_id_list = group_id_list[:1]
    response = request_helper.put_json(groups_url, append_id_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1
    # Try to append an existing group
    response = request_helper.put_json(groups_url, append_id_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1

    # Append the other 2 groups by ID
    append_id_list = group_id_list[1:]
    response = request_helper.put_json(groups_url, append_id_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 2

    # Check that all appended groups are available again
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == len(group_id_list)
    id_list = [group['id'] for group in response.json]
    for id_value in append_id_list:
        assert id_value in id_list


def test_put_related_by_objects(request_helper, default_data, fixture):
    """
    Test appending to a collection of related objects
    by submitting objects.

    """
    fixture.data(ProjectData).setup()

    project = ProjectData.PublicProject

    # Get groups for current project
    groups_url = ProjectResource.get_related_path(project.id, 'groups')
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    group_list = response.json
    assert len(group_list) == 3

    # Remove all related objects
    response = request_helper.delete_json(groups_url, group_list)
    assert response.status_int == 200
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == 0

    # Append a single group by ID
    append_list = group_list[:1]
    response = request_helper.put_json(groups_url, append_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1
    # Try to append an existing group
    response = request_helper.put_json(groups_url, append_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1

    # Append the other 2 groups by ID
    append_list = group_list[1:]
    response = request_helper.put_json(groups_url, append_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 2

    # Check that all appended groups are available again
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == len(group_list)
    id_list = [group['id'] for group in response.json]
    for id_value in [group['id'] for group in append_list]:
        assert id_value in id_list


def test_delete_related_by_ids(helper, request_helper, default_data, fixture):
    """
    Test removal of a collection of related objects by submitting IDs.

    """
    data = fixture.data(ProjectData)
    data.setup()

    project = data.ProjectData.GrouplessPublicProject
    groups_url = ProjectResource.get_related_path(project.id, 'groups')
    group_count = len(TESTS_DATA['groups'])

    # Insert some groups
    url = GroupResource.get_collection_path()
    response = request_helper.post_json(url, TESTS_DATA['groups'])
    assert response.status_int == 200
    # Get the ids for the groups
    group_id_list = [group['id'] for group in response.json]

    # Assign these groups to project
    response = request_helper.put_json(groups_url, group_id_list)
    assert response.status_int == 200

    # Get groups for current project
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(group_id_list) == group_count
    # Check that all ids are right
    for group in response.json:
        assert group['id'] in group_id_list

    # Remove a single group by ID
    delete_id_list = group_id_list[:1]
    response = request_helper.delete_json(groups_url, delete_id_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1

    # Check that deleted group is not available anymore
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == len(group_id_list) - 1
    id_list = [group['id'] for group in response.json]
    assert delete_id_list[0] not in id_list

    # Try to delete an object that does not exist
    response = request_helper.delete_json(groups_url, delete_id_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 0

    # Remove the other group by ID
    delete_id_list = group_id_list[1:2]
    response = request_helper.delete_json(groups_url, delete_id_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1

    # Check that deleted groups are not available anymore
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == len(group_id_list) - group_count
    id_list = [group['id'] for group in response.json]
    for id_value in delete_id_list:
        assert id_value not in id_list


def test_delete_related_by_objects(request_helper, default_data, fixture):
    """
    Test removal of a collection of related objects by submitting objects.

    """
    data = fixture.data(ProjectData)
    data.setup()

    project = data.ProjectData.GrouplessPublicProject
    groups_url = ProjectResource.get_related_path(project.id, 'groups')
    group_count = len(TESTS_DATA['groups'])

    # Insert some groups
    url = GroupResource.get_collection_path()
    response = request_helper.post_json(url, TESTS_DATA['groups'])
    assert response.status_int == 200
    # Get the ids for the groups
    group_id_list = [group['id'] for group in response.json]

    # Assign these groups to project
    response = request_helper.put_json(groups_url, group_id_list)
    assert response.status_int == 200

    # Get groups for current project
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    group_id_list = [group['id'] for group in response.json]
    assert len(group_id_list) == group_count

    # Remove a single group
    delete_list = [{'id': value} for value in group_id_list[:1]]
    response = request_helper.delete_json(groups_url, delete_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1

    # Check that deleted group is not available anymore
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == len(group_id_list) - 1
    id_list = [group['id'] for group in response.json]
    assert delete_list[0]['id'] not in id_list

    # Try to delete an object that does not exist
    response = request_helper.delete_json(groups_url, delete_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 0

    # Remove the other group
    delete_list = [{'id': value} for value in group_id_list[1:]]
    response = request_helper.delete_json(groups_url, delete_list)
    assert response.status_int == 200
    assert isinstance(response.json, dict)
    assert 'info' in response.json
    info = response.json['info']
    assert info.get('count') == 1

    # Check that deleted groups are not available anymore
    response = request_helper.get_json(groups_url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    assert len(response.json) == len(group_id_list) - group_count
    id_list = [group['id'] for group in response.json]
    for value in delete_list:
        assert value['id'] not in id_list
