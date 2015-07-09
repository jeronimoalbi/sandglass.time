from sandglass.time.api.v1.project import ProjectResource

from fixtures import ClientData
from fixtures import GroupData
from fixtures import ProjectData
from fixtures import UserData


def test_project_create_single(helper, request_helper, default_data, fixture):
    """
    Test creation of a project.

    """
    data = fixture.data(ClientData, UserData)
    data.setup()

    project = ProjectData.PublicProject
    project.client_id = data.ClientData.MycroftHolmes.id
    project.user_id = data.UserData.ShepherdBook.id

    url = ProjectResource.get_collection_path()
    project_data = helper.dataset_obj_to_dict(project)
    del project_data['groups']
    response = request_helper.post_json(url, [project_data])
    # All post to collection returns a collection
    assert isinstance(response.json_body, list)
    # User updated information is returned a single item in a list
    project_data = response.json[0]
    project_id = project_data['id']
    assert response.status == '200 OK'

    # Get project by id
    url = ProjectResource.get_member_path(project_id)
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    assert response.json['name'] == project.name

    # Remove the project to allow ficture cleanup
    response = request_helper.delete_json(url)
    assert response.status == '200 OK'
    # Delete returns deleted object data, so, check
    # that values are the same as before it was deleted.
    for name, value in project_data.items():
        assert response.json[name] == value


def test_project_groups(request_helper, default_data, fixture):
    """
    Test projects grouping.

    """
    data = fixture.data(GroupData, ProjectData)
    data.setup()

    project = data.ProjectData.PublicProject
    groups = project.groups
    group_id_list = [group.id for group in groups]

    # Get groups for a project
    url = ProjectResource.get_related_path(project['id'], 'groups')
    response = request_helper.get_json(url)
    assert response.status_int == 200
    assert isinstance(response.json_body, list)
    # Check that response got the right number of groups
    assert len(response.json_body) == len(group_id_list)
    # Check returned groups are the ones assigned to current project
    for group in response.json_body:
        assert group['id'] in group_id_list
