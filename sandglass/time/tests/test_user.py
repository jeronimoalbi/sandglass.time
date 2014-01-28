import sandglass.time

# TODO Improve Tests: Tests for multiple deletion, multiple getting


class UserTest(sandglass.time.tests.BaseFunctionalTest):

    def test_user_create(self):
        """
        Test creation of a single user
        """
        # Create a user
        userlist = []
        userlist.append({
            "email": "timeywimey@wienfluss.net",
            "first_name": "Dr",
            "last_name": "Who"
        })

        create_response = self.testapp.post_json('/time/api/v1/users/',
                                                 userlist,
                                                 status=200)
        created_id = create_response.json[0]['id']
        json = create_response.json

        self.failUnless(created_id.__class__ == int)

        self.assertTrue(json[0]['first_name'] == 'Dr',
                        'First name should have been "Dr"')
        self.assertTrue(json[0]['last_name'] == 'Who',
                        'Last name should have been "Who"')
        self.assertTrue(json[0]['email'] == 'timeywimey@wienfluss.net',
                        'Email should have been "timeywimey@wienfluss.net"')

    def test_user_create_multiple(self):
        """
        Tests creation of multiple users
        """

        userlist = []
        userlist.append({
            "email": "humpdydumpdy@wienfluss.net",
            "first_name": "James William",
            "last_name": "Elliot"
        })
        userlist.append({
            "email": "ruggedlyhandsome@wienfluss.net",
            "first_name": "Rick",
            "last_name": "Castle"
        })

        create_response = self.testapp.post_json('/time/api/v1/users/',
                                                 userlist,
                                                 status=200)
        json = create_response.json
        self.failUnless(len(json) == 2,
                        'Not enough entries in response, expected 2')

        # Assert creation of first user
        self.assertTrue(json[0]['first_name'] == 'James William',
                        'First name should have been "James William"')
        self.assertTrue(json[0]['last_name'] == 'Elliot',
                        'Last name should have been "Elliot"')
        self.assertTrue(json[0]['email'] == 'humpdydumpdy@wienfluss.net',
                        'Email should have been "humpdydumpdy@wienfluss.net"')

        # Assert creation of first user
        self.assertTrue(json[1]['first_name'] == 'Rick',
                        'First name should have been "Rick')
        self.assertTrue(json[1]['last_name'] == 'Castle',
                        'Last name should have been "Castle"')
        self.assertTrue(json[1]['email'] == 'ruggedlyhandsome@wienfluss.net',
                        'Email should have been "ruggedlyhandsome@wienfluss.net"')

    def test_user_delete(self):
        """
        Test deleting a user
        """
        # Create a user
        userlist = []
        userlist.append({
            "email": "wibblywobbly@wienfluss.net",
            "first_name": "The",
            "last_name": "Tardis"
        })

        create_response = self.testapp.post_json('/time/api/v1/users/',
                                                 userlist,
                                                 status=200)
        created_id = create_response.json[0]['id']

        # Delete that user again
        delete_response = self.testapp.delete_json(
            '/time/api/v1/users/{}/'.format(created_id), status=200)

        self.testapp.get(
            '/time/api/v1/users/{}/'.format(created_id), status=404)

    def test_get_user(self):
        """
        Test fetching a user by ID
        """

        # Create a third user
        userlist = []
        userlist.append({
            "email": "ittybitty@wienfluss.net",
            "first_name": "Amilia",
            "last_name": "Pond"
        })

        create_response = self.testapp.post_json('/time/api/v1/users/',
                                                 userlist,
                                                 status=200)
        created_id = create_response.json[0]['id']

        get_response = self.testapp.get(
            '/time/api/v1/users/{}/'.format(created_id), status=200)
