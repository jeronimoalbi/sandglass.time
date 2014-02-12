import sandglass.time
import unittest

from pyramid.exceptions import NotFound
# TODO Improve Tests: Tests for multiple deletion, multiple getting

@unittest.skip("showing class skipping")
class UserTest(sandglass.time.tests.FunctionalTestCase):

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