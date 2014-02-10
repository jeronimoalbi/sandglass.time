import sandglass.time
# TODO Improve Tests: Tests for multiple deletion, multiple getting


class ProjectTest(sandglass.time.tests.IntegrationTestCase):

    client_list = []
    client_list.append({'name': 'Henry Knight'})

    project_list = []
    project_list.append({
        "name": "Mysterious Hound",
        "parent_id": "0",
        "client_id": "0",
        "user_id": "1",
    })

    def test_project_create(self):
        """
        Test creation of a project
        """

        # first we need a client for that project
        (client_id, json) = self._create(
            '/time/api/v1/clients/',
            [self.client_list[0]])

        self.project_list[0]['client_id'] = client_id

        # now we create that project
        (created_id, json) = self._create(
            '/time/api/v1/projects/',
            [self.project_list[0]])

        self.failUnless(created_id.__class__ == int)

        self.assertTrue(json[0]['name'] == self.project_list[0]['name'],
                        'Name should have been "{}", was "{}"'
                        .format(self.project_list[0]['name'], json[0]['name']))
