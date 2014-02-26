from sandglass.time.api.v1.project import ProjectResource

from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests import fixture
from sandglass.time.tests.fixtures import ClientData
from sandglass.time.tests.fixtures import ProjectData
from sandglass.time.tests.fixtures import UserData


class ProjectResourceTest(FunctionalTestCase):

    # Use authentication for each request by default
    require_authorization = True

    @fixture(ClientData, UserData)
    def test_project_create_single(self):
        """
        Test creation of a project.

        """
        data = self.fixture_data
        project = ProjectData.baskerville_hound
        project.client_id = data.data['ClientData']['mycroft_holmes']['id']
        project.user_id = data.data['UserData']['shepherd_book']['id']

        url = ProjectResource.get_collection_path()

        response = self.post_json(url, project.to_dict())
        # All post to collection returns a collection
        self.assertTrue(isinstance(response.json, list))
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
