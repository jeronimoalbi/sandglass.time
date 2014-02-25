from sandglass.time.api.v1.project import ProjectResource

from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests import fixture
from sandglass.time.tests.fixtures import ProjectData, ClientData, UserData
from sandglass.time.tests import AuthData


class ProjectResourceTest(FunctionalTestCase):

    # Use authentication for each request by default
    require_authorization = True

    @fixture(AuthData, ClientData, UserData)
    def test_project_create_single(self, data):
        """
        Test creation of a project
        """
        project = ProjectData.baskerville_hound
        project.client_id = data.data['ClientData']['mycroft_holmes']['id']
        project.user_id = data.data['UserData']['shepherd_book']['id']

        url = ProjectResource.get_collection_path()

        response = self.post_json(url,project.to_dict())
        created_id = response.json['id']

        # assert response is ok
        self.assertEqual(response.status, '200 OK')

        url = ProjectResource.get_member_path(created_id)
        response = self.get_json(url)

        # assert response is ok
        self.assertEqual(response.status, '200 OK')
        self.assertEqual(response.json['name'], project.name)

        # Cleanup: Delete Project
        response = self.delete_json(url)
