from sandglass.time.api.v1.project import ProjectResource

from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests import fixture

from .fixtures import ClientData
from .fixtures import GroupData
from .fixtures import ProjectData
from .fixtures import UserData


class ProjectResourceTest(FunctionalTestCase):

    # Use authentication for each request by default
    require_authorization = True

    @fixture(ClientData, UserData)
    def test_project_create_single(self):
        """
        Test creation of a project.

        """
        data = self.fixture_data.data
        project = ProjectData.BaskervilleHound
        project.client_id = data['ClientData']['MycroftHolmes']['id']
        project.user_id = data['UserData']['ShepherdBook']['id']

        url = ProjectResource.get_collection_path()

        response = self.post_json(url, [project.to_dict()])
        # All post to collection returns a collection
        self.assertTrue(isinstance(response.json_body, list))
        # User updated information is returned a single item in a list
        project_data = response.json[0]
        created_id = project_data['id']

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        url = ProjectResource.get_member_path(created_id)
        response = self.get_json(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['name'], project.name)

        # Cleanup: Delete Project
        response = self.delete_json(url)

    @fixture(GroupData, ProjectData)
    def test_project_groups(self):
        """
        Test projects grouping.

        """
        data = self.fixture_data.data
        project = data['ProjectData']['PublicProject']
        groups = project['groups']
        group_id_list = [group.id for group in groups]
        # Get groups for a project
        url = ProjectResource.get_related_path(project['id'], 'groups')
        response = self.get_json(url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        # Check that response got the right number of groups
        self.assertEqual(len(response.json_body), len(group_id_list))
        # Check returned groups are the ones assigned to current project
        for group in response.json_body:
            self.assertTrue(group['id'] in group_id_list)
