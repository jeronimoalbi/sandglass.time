from sandglass.time.tests import FunctionalTestCase
from sandglass.time.api.v1.task import TaskResource
from sandglass.time.tests import fixture

from .fixtures import TaskData
from .fixtures import ProjectData


class TaskResourceTest(FunctionalTestCase):
    """
    Functional tests for Task resource.

    """
    # Use authentication for each request by default
    require_authorization = True

    def get_task_data(self):
        user = self.fixture_data['UserData']['DrWho']
        project = self.fixture_data['ProjectData']['PublicProject']
        return {
            'name': u"Test task",
            'user_id': user['id'],
            'project_id': project['id'],
        }

    @fixture(ProjectData)
    def test_create_single_task(self):
        """
        Create a single task using the API.

        """
        task_data = self.get_task_data()
        url = TaskResource.get_collection_path()
        # Create the new task
        response = self.post_json(url, [task_data])
        # Check for success, and that body contains a list with one element
        self.assertTrue(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, list))
        self.assertEqual(len(response.json_body), 1)
        # Check that task has a valid ID value
        task = response.json_body[0]
        self.assertTrue('id' in task)
        self.assertTrue(isinstance(task['id'], int))

    def test_update_single_task(self):
        """
        Update a single task using the API.

        """

    def test_delete_single_task(self):
        """
        Delete a single task using the API.

        """

    @fixture(TaskData)
    def test_task_with_project(self):
        """
        Test a task with a projects.

        """
        task = self.fixture_data['TaskData']['Backend']
        url = TaskResource.get_related_path(task['id'], 'project')
        # Get task project data
        response = self.get_json(url)
        self.assertTrue(response.status_int, 200)
        self.assertTrue(isinstance(response.json_body, dict))

        # Check that project is the same as the requested task data
        project = response.json_body
        self.assertEqual(task.project.id, project['id'])
