from sandglass.time.tests import FunctionalTestCase
from sandglass.time.tests.fixtures import UserData, ClientData, ProjectData
from sandglass.time.tests import fixture
import unittest

@unittest.skip("showing class skipping")
class ClientResourceTest(FunctionalTestCase):

    """
    Functional tests for User resource.

    """

    @fixture(ClientData)
    def test_create_single_client(data, self):
        self.fail()

    @fixture(ProjectData)
    def test_create_single_client2(data,self):
        self.fail()