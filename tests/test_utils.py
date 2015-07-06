from sandglass.time import utils
from sandglass.time.tests import BaseTestCase


class UtilsTest(BaseTestCase):
    """
    Test case for `utils` module.

    """
    def test_is_valid_email(self):
        """
        Test email checking function `is_valid_email`.

        """
        # Test some invalid values
        fail_values = ('invalid @ email', 1, True, {}, None)
        for value in fail_values:
            is_valid = utils.is_valid_email(value)
            self.assertFalse(is_valid)

        # Test valid value
        is_valid = utils.is_valid_email('valid@email.org')
        self.assertTrue(is_valid)

    def test_get_settings(self):
        """
        Test function `get_settings` to get application settings.

        """
        # Initialize Pyramid testing environment support and get settings
        self.setup_pyramid_testing()
        settings = utils.get_settings()

        # Settings should be a non empty dictionary
        self.assertIsInstance(settings, dict)
        self.assertGreater(settings, 0)

        # Cleanup Pyramid testing environment
        self.teardown_pyramid_testing()

    def test_camelcase_to_underscore(self):
        """
        Test camel case to underscore convert function.

        """
        # Check "falsy" values
        text = utils.camelcase_to_underscore('')
        self.assertEqual(text, '')
        text = utils.camelcase_to_underscore(False)
        self.assertEqual(text, False)

        text = utils.camelcase_to_underscore('testCamelCaseName')
        self.assertEqual(text, 'test_camel_case_name')
        text = utils.camelcase_to_underscore('_testCamelCaseName_end')
        self.assertEqual(text, '_test_camel_case_name_end')
        text = utils.camelcase_to_underscore('test_camel_case_name')
        self.assertEqual(text, 'test_camel_case_name')

    def test_underscore_to_camelcase(self):
        """
        Test underscore to camel case convert function.

        """
        # Check "falsy" values
        text = utils.underscore_to_camelcase('')
        self.assertEqual(text, '')
        text = utils.underscore_to_camelcase(False)
        self.assertEqual(text, False)

        text = utils.underscore_to_camelcase('test_camel_case_name')
        self.assertEqual(text, 'testCamelCaseName')
        text = utils.underscore_to_camelcase('_test_camel_case_name_End')
        self.assertEqual(text, '_testCamelCaseNameEnd')
        text = utils.underscore_to_camelcase('testCamelCaseName')
        self.assertEqual(text, 'testCamelCaseName')

    def test_camelcase_dict(self):
        """
        Test convertion of dict keys to camel case.

        """
        test_dict = utils.camelcase_dict({
            'a_name': 0,
            'anotherName': 0,
            'Test_name': 0})
        self.assertIn('aName', test_dict)
        self.assertIn('anotherName', test_dict)
        self.assertIn('testName', test_dict)

    def test_underscore_dict(self):
        """
        Test convertion of dict keys to underscore.

        """
        test_dict = utils.underscore_dict({
            'a_name': 0,
            'anotherName': 0,
            'Test_name': 0})
        self.assertIn('a_name', test_dict)
        self.assertIn('another_name', test_dict)
        self.assertIn('test_name', test_dict)

    def test_mixedmethod(self):
        """
        Test `mixedmethod` decorator for class&instance methods.

        This decorator allows a class to implement a single method
        that can be called as instance or class method.

        """
        class TestClass(object):
            @utils.mixedmethod
            def what_am_i(obj):
                if isinstance(obj, TestClass):
                    return 'instance'
                elif issubclass(obj, TestClass):
                    return 'class'

        self.assertEqual(TestClass.what_am_i(), 'class')
        test_obj = TestClass()
        self.assertEqual(test_obj.what_am_i(), 'instance')

    def test_route_path(self):
        """
        Test route URL path generation.

        """
        # TODO: This test should not depend on an API version
        prefix = '/time/api/v1'
        member = 'users'
        pk = '1'
        related = 'tags'

        self.setup_pyramid_testing()
        path = utils.route_path('api.rest.collection', member=member)
        self.assertEqual(path, prefix + '/users/')
        path = utils.route_path('api.rest.member', member=member, pk=pk)
        self.assertEqual(path, prefix + '/users/1/')
        path = utils.route_path(
            'api.rest.related', member=member, pk=pk, related_name=related)
        self.assertEqual(path, prefix + '/users/1/tags/')
        self.teardown_pyramid_testing()

    def test_generate_random_hash(self):
        """
        Test random hash generation function `generate_random_hash`.

        """
        hash = utils.generate_random_hash(salt=u'fdskjgs', hash='sha1')
        self.assertIsInstance(hash, basestring)
        self.assertTrue(len(hash), 40)
        try:
            utils.generate_random_hash(hash='invalid_name')
        except Exception:
            # Invalid hashing algorithms should raise an exception
            pass
        else:
            self.fail('Exception espected for invalid hash names')

    def test_get_app_namespace(self):
        """
        Check that function `get_app_namespace` gets proper app namespaces.

        """
        class LocalClass(object):
            pass

        # Check a python module string
        namespace = utils.get_app_namespace('sandglass.app_namespace.module')
        self.assertEqual(namespace, 'app_namespace')
        # Check a sandglass.time module
        namespace = utils.get_app_namespace(utils)
        self.assertEqual(namespace, 'time')
        # Check a class defined in sandglass.time
        namespace = utils.get_app_namespace(LocalClass)
        self.assertEqual(namespace, 'time')

        # Check non sandglass python module string
        try:
            utils.get_app_namespace('foreign.namespace.module')
        except Exception:
            # Non sandglass prefixed modules should raise an exception
            pass
        else:
            self.fail('Excpedted exception for non sandglass application')

        # Check a non sandglass module
        import os
        try:
            utils.get_app_namespace(os.path)
        except Exception:
            # Non sandglass prefixed modules should raise an exception
            pass
        else:
            self.fail('Excpedted exception for non sandglass application')
