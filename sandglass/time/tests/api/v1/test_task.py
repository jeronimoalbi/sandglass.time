from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests import fixture

from .fixtures import TaskData


class TaskResourceTest(FunctionalTestCase):
    """
    Functional tests for Task resource.

    """
    # Use authentication for each request by default
    require_authorization = True

    def test_create_single_task(self):
        """
        Create a single task using the API.

        """

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
