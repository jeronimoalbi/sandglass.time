from sandglass.time.api.v1.group import GroupResource
from sandglass.time.api.v1.project import ProjectResource
from sandglass.time.models.permission import Permission


def test_project_create_single(request_helper, default_data, session):
    """
    Test creation of a project.

    """
    project = default_data.projects.public_project
    session.add(project)

    url = ProjectResource.get_collection_path()
    project_data = dict(project)
    project_data['id'] = None
    response = request_helper.post_json(url, [project_data])
    # All post to collection returns a collection
    assert isinstance(response.json, list)
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


def test_project_groups(request_helper, default_data, session):
    """
    Test projects grouping.

    """
    project = default_data.projects.public_project
    session.add(project)
    groups = project.groups
    group_id_list = [group.id for group in groups]

    # Get groups for a project
    url = ProjectResource.get_related_path(project.id, 'groups')
    response = request_helper.get_json(url)
    assert response.status_int == 200
    assert isinstance(response.json, list)
    # Check that response got the right number of groups
    assert len(response.json) == len(group_id_list)
    # Check returned groups are the ones assigned to current project
    for group in response.json:
        assert group['id'] in group_id_list


def test_project_private_query_filter(request_helper, default_data, session):
    """
    Test that private projects are not filtered for admin users.

    Private projects should only be visible to the user who created
    the project, or to users with right permission.

    """
    # Get the number of visible projects for the admin user
    url = ProjectResource.get_collection_path()
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    admin_visible_count = len(response.json)

    # Check that a non admin user get less projects
    user = default_data.users.dr_who
    session.add(user)
    request_helper.auth_as_user(user)
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert admin_visible_count > len(response.json)

    # Allow user to see private projects by adding view
    # private project permission to a group user belongs to.
    group = default_data.groups.employee
    session.add(group)
    query = Permission.query(session=session)
    query = query.filter_by(name='time.project.view_private')
    permission = query.one()
    group_perms_url = GroupResource.get_related_path(group.id, 'permissions')
    response = request_helper.put_json(group_perms_url, [permission.id])
    assert response.status == '200 OK'

    # Check that a non admin user now can see the
    # same number of projects as an admin user.
    response = request_helper.get_json(url)
    assert response.status == '200 OK'
    assert isinstance(response.json, list)
    assert admin_visible_count == len(response.json)
