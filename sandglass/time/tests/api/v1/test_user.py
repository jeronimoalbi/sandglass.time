from sandglass.time.api.v1.user import UserResource
from sandglass.time.tests import FunctionalTestCase


USERS_DATA = [
    {"email": "timeywimey@wienfluss.net",
     "first_name": "Dr",
     "last_name": "Who"},
    {"email": "humpdydumpdy@wienfluss.net",
     "first_name": "James William",
     "last_name": "Elliot"},
    {"email": "ruggedlyhandsome@wienfluss.net",
     "first_name": "Rick",
     "last_name": "Castle"},
]


class UserResourceTest(FunctionalTestCase):
    """
    Integration tests for User resource.

    """
    def setUp(self):
        super(UserResourceTest, self).setUp()
        self.user_list = []

    def tearDown(self):
        del self.user_list
        super(UserResourceTest, self).tearDown()

    def test_create_single_user(self):
        user = USERS_DATA[0]
        url = UserResource.get_collection_path()
        response = self.app.post_json(url, [user])

    def test_update_single_user(self):
        self.fail()

    def test_get_user(self):
        self.fail()

    def test_delete_single_user(self):
        self.fail()

    def test_create_multiple_users(self):
        self.fail()

    def test_update_multiple_users(self):
        self.fail()

    def test_get_user_by_credentials(self):
        self.fail()

    def test_delete_multiple_users(self):
        self.fail()
