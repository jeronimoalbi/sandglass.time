import sandglass.time

from pyramid.exceptions import NotFound

# TODO Improve Tests: Tests for multiple deletion, multiple getting


class ClientTest(sandglass.time.tests.IntegrationTestCase):

    clients = ['Sherlock Holmes',
               'Mycroft Holmes',
               'Dr. John Watson',
               'DI Greg Lestrade',
               'James Moriarty',
               'Charles Augustus Magnussen']
    client_list = []
    for client in clients:
        client_list.append({'name': client})

    def test_client_create(self):
        """
        Test creation of a client
        """
        (created_id, json) = self._create(
            '/time/api/v1/clients/',
            [self.client_list[0]])
        self.failUnless(created_id.__class__ == int)

        self.assertTrue(json[0]['name'] == self.client_list[0]['name'],
                        'Name should have been "{}", was "{}"'
                        .format(self.client_list[0]['name'], json[0]['name']))

    def test_client_create_multiple(self):
        """
        Test creation of multiple activities
        """
        (created_id, json) = self._create(
            '/time/api/v1/clients/',
            [self.client_list[1],
             self.client_list[2]])

        self.failUnless(len(json) == 2,
                        'Not enough entries in response, expected 2')

        self.failUnless(json[0]['id'].__class__ == int)

        self.assertTrue(json[0]['name'] == self.client_list[1]['name'],
                        'Name should have been "{}", was "{}"'
                        .format(self.client_list[1]['name'], json[0]['name']))
        self.assertTrue(json[1]['name'] == self.client_list[2]['name'],
                        'Name should have been "{}", was "{}"'
                        .format(self.client_list[2]['name'], json[1]['name']))

    def test_client_delete(self):
        """
        Test deletion of a client
        """
        # Create a user
        (created_id, json) = self._create(
            '/time/api/v1/clients/',
            [self.client_list[3]])

        # Delete that user again
        self.app.delete_json(
            '/time/api/v1/clients/{}/'.format(created_id), status=200)
        
        with self.assertRaises(NotFound): 
            self.app.get('/time/api/v1/clients/{}/'.format(created_id))



    def test_client_update(self):
        """
        Test updating of a client
        """
        (created_id, json) = self._create(
            '/time/api/v1/clients/',
            [self.client_list[4]])

        update = {
            "name": "Irene Adler",
        }

        # Update that user
        update_response = self.app.put_json(
            '/time/api/v1/clients/{}/'.format(created_id),
            update,
            status=200
        )

        get_response = self.app.get(
            '/time/api/v1/clients/{}/'.format(created_id), status=200)

        json = get_response.json
        self.assertTrue(json['name'] == 'Irene Adler',
                        'Expected name to be "{}", was "{}"'
            .format(update['name'], json['name']))

    def test_client_get(self):
        """
        Test getting of a client
        """
        (created_id, json) = self._create(
            '/time/api/v1/clients/',
            [self.client_list[5]])

        get_response = self.app.get(
            '/time/api/v1/clients/{}/'.format(created_id), status=200)

        json = get_response.json

        self.assertTrue(json['name'] == self.client_list[5]['name'],
                        'Expected name to be "{}", was "{}"'
                        .format(self.client_list[5]['name'], json['name'])
                        )
