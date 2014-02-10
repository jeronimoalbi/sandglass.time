import unittest
from datetime import datetime
from pyramid import testing

from sandglass.time.forms.activity import ActivitySchema
from sandglass.time.models.activity import ACTIVITY_WORKING


class FormActivityTest(unittest.TestCase):
    """Test class for sandglass.time.forms.activity

    """
    def setUp(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        self.activity = {
                         'id': 1,
                         'user_id': 1,
                         'description':'Activity description.',
                         'start':'2014-01-23 13:51:58.354288',
                         'end':'2014-01-23 13:52:00.354288',
                         'activity_type': ACTIVITY_WORKING,
                         'project_id': '123',
                         'task_id': '456',
                        }

    def tearDown(self):
        testing.tearDown()

    def test_activity_schema(self):
        cstruct = self.activity
        schema = ActivitySchema()
        deserialized = schema.deserialize(cstruct)

        self.assertTrue(isinstance(deserialized['description'], unicode))
        self.assertTrue(isinstance(deserialized['start'], datetime))
        self.assertTrue(isinstance(deserialized['end'], datetime))
        self.assertTrue(isinstance(deserialized['activity_type'], unicode))
        self.assertEqual(deserialized['project_id'], 123)
        self.assertEqual(deserialized['task_id'], 456)
