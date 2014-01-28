import sandglass.time

# TODO Improve Tests: Tests for multiple deletion, multiple getting


class ClientTest(sandglass.time.tests.BaseFunctionalTest):

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
        create_response = self.testapp.post_json('/time/api/v1/clients/',
                                                 [self.client_list[0]],
                                                 status=200)
        created_id = create_response.json[0]['id']
        json = create_response.json

        self.failUnless(created_id.__class__ == int)

        self.assertTrue(json[0]['name'] == self.client_list[0]['name'],
                        'Name should have been "{}", was "{}"'
                        .format(self.client_list[0]['name'], json[0]['name']))

    def test_client_create_multiple(self):
        """
        Test creation of multiple activities
        """
        create_response = self.testapp.post_json('/time/api/v1/clients/',
                                                 [self.client_list[1],
                                                  self.client_list[2]],
                                                 status=200)
        json = create_response.json
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
        create_response = self.testapp.post_json('/time/api/v1/clients/',
                                                 [self.client_list[3]],
                                                 status=200)
        created_id = create_response.json[0]['id']

        # Delete that user again
        self.testapp.delete_json(
            '/time/api/v1/clients/{}/'.format(created_id), status=200)

        self.testapp.get(
            '/time/api/v1/clients/{}/'.format(created_id), status=404)

    def test_client_update(self):
        """
        Test updating of a client
        """
        create_response = self.testapp.post_json('/time/api/v1/clients/',
                                                 [self.client_list[4]],
                                                 status=200)
        created_id = create_response.json[0]['id']

        update = {
            "name": "Irene Adler",
        }

        # Update that user
        update_response = self.testapp.put_json(
            '/time/api/v1/clients/{}/'.format(created_id),
            update,
            status=200
        )

        get_response = self.testapp.get(
            '/time/api/v1/clients/{}/'.format(created_id), status=200)

        json = get_response.json
        self.assertTrue(json['name'] == 'Irene Adler',
                        'Expected name to be "{}", was "{}"'
            .format(update['name'], json['name']))

    def test_client_get(self):
        """
        Test getting of a client
        """
        create_response = self.testapp.post_json('/time/api/v1/clients/',
                                                 [self.client_list[5]],
                                                 status=200)
        created_id = create_response.json[0]['id']

        get_response = self.testapp.get(
            '/time/api/v1/clients/{}/'.format(created_id), status=200)

        json = get_response.json

        self.assertTrue(json['name'] == self.client_list[5]['name'],
                        'Expected name to be "{}", was "{}"'
                        .format(self.client_list[5]['name'], json['name'])
                        )
