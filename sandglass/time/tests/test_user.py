import sandglass.time

# TODO Improve Tests: Tests for multiple deletion, multiple getting


class UserTest(sandglass.time.tests.BaseFunctionalTest):

    user_list = []
    user_list.append({
        "email": "timeywimey@wienfluss.net",
        "first_name": "Dr",
        "last_name": "Who"
    })
    user_list.append({
        "email": "humpdydumpdy@wienfluss.net",
        "first_name": "James William",
        "last_name": "Elliot"
    })
    user_list.append({
        "email": "ruggedlyhandsome@wienfluss.net",
        "first_name": "Rick",
        "last_name": "Castle"
    })
    user_list.append({
        "email": "wibblywobbly@wienfluss.net",
        "first_name": "The",
        "last_name": "Tardis"
    })
    user_list.append({
        "email": "strangecase@wienfluss.net",
        "first_name": "Dr.",
        "last_name": "Jekyll"
    })
    user_list.append({
        "email": "specialhell@serenity.org",
        "first_name": "Shepherd",
        "last_name": "Book"
    })

    def test_user_create(self):
        """
        Test creation of a single user
        """
        (created_id, json) = self._create(
            '/time/api/v1/users/',
            [self.user_list[0]])

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

        (created_id, json) = self._create(
            '/time/api/v1/users/',
            [self.user_list[1],
             self.user_list[2]])

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
        (created_id, json) = self._create(
            '/time/api/v1/users/',
            [self.user_list[3]])

        # Delete that user again
        self.testapp.delete_json(
            '/time/api/v1/users/{}/'.format(created_id), status=200)

        self.testapp.get(
            '/time/api/v1/users/{}/'.format(created_id), status=404)

    def test_user_update(self):
        """
        Test updating a user
        """
        (created_id, json) = self._create(
            '/time/api/v1/users/',
            [self.user_list[4]])

        update = {
            "email": "strangecase@wienfluss.net",
            "first_name": "Mr.",
            "last_name": "Hyde",
        }

        # Update that user
        update_response = self.testapp.put_json(
            '/time/api/v1/users/{}/'.format(created_id),
            update,
            status=200
        )

        get_response = self.testapp.get(
            '/time/api/v1/users/{}/'.format(created_id), status=200)

        json = get_response.json
        self.assertTrue(json['first_name'] == 'Mr.',
                        'Expected first_name to be "Mr.", was "{}"'
            .format(json['first_name']))
        self.assertTrue(json['last_name'] == 'Hyde',
                        'Expected last_name to be "Hyde", was "{}"'
            .format(json['last_name']))

    def test_user_get(self):
        """
        Test fetching a user by ID
        """

        (created_id, json) = self._create(
            '/time/api/v1/users/',
            [self.user_list[5]])

        get_response = self.testapp.get(
            '/time/api/v1/users/{}/'.format(created_id), status=200)

        json = get_response.json

        self.assertTrue(json['email'] == 'specialhell@serenity.org',
                        'Expected email to be "{}", was "{}"'
            .format(self.user_list[5]['email'], json['email']))
        self.assertTrue(json['first_name'] == 'Shepherd',
                        'Expected first_name to be "Shepherd", was "{}"'
            .format(json['first_name']))
        self.assertTrue(json['last_name'] == 'Book',
                        'Expected last_name to be "Book", was "{}"'
            .format(json['last_name']))
