from sandglass.time.api.v1.project import ProjectResource

from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests import fixture

from .fixtures import ProjectData


class ModelResourceTest(FunctionalTestCase):
    """
    Functional test case for model resources.

    """
    # Use authentication for each request by default
    require_authorization = True

    @fixture(ProjectData)
    def test_delete_related_invalid_type(self):
        """
        Check that an error is returned when deleting related with
        wrong request content type.

        """
        project = ProjectData.PublicProject
        # Try to delete a group using an integer
        groups_url = ProjectResource.get_related_path(project.id, 'groups')
        response = self.delete_json(groups_url, 1)
        self.assertEqual(response.status_int, 500)
        self.assertTrue(isinstance(response.json_body, dict))
        # An error with VALIDATION_ERROR houls be returned
        self.assertTrue('error' in response.json_body)
        error = response.json_body['error']
        self.assertEqual(error['code'], 'VALIDATION_ERROR')

    @fixture(ProjectData)
    def test_delete_related_by_ids(self):
        """
        Test removal of a collection of related objects by submitting IDs.

        """
        project = ProjectData.PublicProject

        # Get groups for current project
        groups_url = ProjectResource.get_related_path(project.id, 'groups')
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        group_id_list = [group['id'] for group in response.json_body]
        self.assertEqual(len(group_id_list), 3)

        # Remove a single group by ID
        delete_id_list = group_id_list[:1]
        response = self.delete_json(groups_url, delete_id_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 1)
        # Check that deleted group is not available anymore
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), len(group_id_list) - 1)
        id_list = [group['id'] for group in response.json_body]
        self.assertTrue(delete_id_list[0] not in id_list)
        # Try to delete an object that does not exist
        response = self.delete_json(groups_url, delete_id_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 0)

        # Remove the other 2 groups by ID
        delete_id_list = group_id_list[1:]
        response = self.delete_json(groups_url, delete_id_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 2)
        # Check that deleted groups are not available anymore
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), len(group_id_list) - 3)
        id_list = [group['id'] for group in response.json_body]
        for id_value in delete_id_list:
            self.assertTrue(id_value not in id_list)

    @fixture(ProjectData)
    def test_delete_related_by_objects(self):
        """
        Test removal of a collection of related objects by submitting objects.

        """
        project = ProjectData.PublicProject

        # Get groups for current project
        groups_url = ProjectResource.get_related_path(project.id, 'groups')
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        group_id_list = [group['id'] for group in response.json_body]
        self.assertEqual(len(group_id_list), 3)

        # Remove a single group by ID
        delete_list = [{'id': value} for value in group_id_list[:1]]
        response = self.delete_json(groups_url, delete_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 1)
        # Check that deleted group is not available anymore
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), len(group_id_list) - 1)
        id_list = [group['id'] for group in response.json_body]
        self.assertTrue(delete_list[0]['id'] not in id_list)
        # Try to delete an object that does not exist
        response = self.delete_json(groups_url, delete_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 0)

        # Remove the other 2 groups by ID
        delete_list = [{'id': value} for value in group_id_list[1:]]
        response = self.delete_json(groups_url, delete_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 2)
        # Check that deleted groups are not available anymore
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), len(group_id_list) - 3)
        id_list = [group['id'] for group in response.json_body]
        for value in delete_list:
            self.assertTrue(value['id'] not in id_list)

    @fixture(ProjectData)
    def test_put_related_invalid_type(self):
        """
        Check that an error is returned when appending related with
        wrong request content type.

        """
        project = ProjectData.PublicProject
        # Try to delete a group using an integer
        groups_url = ProjectResource.get_related_path(project.id, 'groups')
        response = self.put_json(groups_url, 1)
        self.assertEqual(response.status_int, 500)
        self.assertTrue(isinstance(response.json_body, dict))
        # An error with VALIDATION_ERROR houls be returned
        self.assertTrue('error' in response.json_body)
        error = response.json_body['error']
        self.assertEqual(error['code'], 'VALIDATION_ERROR')

    @fixture(ProjectData)
    def test_put_related_by_ids(self):
        """
        Test appending to a collection of related objects by submitting IDs.

        """
        project = ProjectData.PublicProject

        # Get groups for current project
        groups_url = ProjectResource.get_related_path(project.id, 'groups')
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        group_id_list = [group['id'] for group in response.json_body]
        self.assertEqual(len(group_id_list), 3)

        # Remove all related objects
        response = self.delete_json(groups_url, group_id_list)
        self.assertEqual(response.status_int, 200)
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), 0)

        # Append a single group by ID
        append_id_list = group_id_list[:1]
        response = self.put_json(groups_url, append_id_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 1)
        # Try to append an existing group
        response = self.put_json(groups_url, append_id_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 1)

        # Append the other 2 groups by ID
        append_id_list = group_id_list[1:]
        response = self.put_json(groups_url, append_id_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 2)

        # Check that all appended groups are available again
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), len(group_id_list))
        id_list = [group['id'] for group in response.json_body]
        for id_value in append_id_list:
            self.assertTrue(id_value in id_list)

    @fixture(ProjectData)
    def test_put_related_by_objects(self):
        """
        Test appending to a collection of related objects
        by submitting objects.

        """
        project = ProjectData.PublicProject

        # Get groups for current project
        groups_url = ProjectResource.get_related_path(project.id, 'groups')
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        group_list = response.json_body
        self.assertEqual(len(group_list), 3)

        # Remove all related objects
        response = self.delete_json(groups_url, group_list)
        self.assertEqual(response.status_int, 200)
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), 0)

        # Append a single group by ID
        append_list = group_list[:1]
        response = self.put_json(groups_url, append_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 1)
        # Try to append an existing group
        response = self.put_json(groups_url, append_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 1)

        # Append the other 2 groups by ID
        append_list = group_list[1:]
        response = self.put_json(groups_url, append_list)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))
        self.assertTrue('info' in response.json_body)
        info = response.json_body['info']
        self.assertEqual(info.get('count'), 2)

        # Check that all appended groups are available again
        response = self.get_json(groups_url)
        self.assertEqual(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), len(group_list))
        id_list = [group['id'] for group in response.json_body]
        for id_value in [group['id'] for group in append_list]:
            self.assertTrue(id_value in id_list)
