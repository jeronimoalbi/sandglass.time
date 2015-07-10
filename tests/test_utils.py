import pytest

from sandglass.time import utils


@pytest.mark.usefixtures('default_data')
def test_mix(mixer):
    import ipdb;ipdb.set_trace() 


def test_is_valid_email():
    """
    Test email checking function `is_valid_email`.

    """
    # Test some invalid values
    fail_values = ('invalid @ email', 1, True, {}, None)
    for value in fail_values:
        is_valid = utils.is_valid_email(value)
        assert is_valid is False

    # Test valid value
    is_valid = utils.is_valid_email('valid@email.org')
    assert is_valid


def test_get_settings(config):
    """
    Test function `get_settings` to get application settings.

    """
    settings = utils.get_settings()
    # Settings should be a non empty dictionary
    assert isinstance(settings, dict)
    assert settings > 0


def test_camelcase_to_underscore():
    """
    Test camel case to underscore convert function.

    """
    # Check "falsy" values
    text = utils.camelcase_to_underscore('')
    assert text == ''
    text = utils.camelcase_to_underscore(False)
    assert text is False

    text = utils.camelcase_to_underscore('testCamelCaseName')
    assert text == 'test_camel_case_name'
    text = utils.camelcase_to_underscore('_testCamelCaseName_end')
    assert text == '_test_camel_case_name_end'
    text = utils.camelcase_to_underscore('test_camel_case_name')
    assert text == 'test_camel_case_name'


def test_underscore_to_camelcase():
    """
    Test underscore to camel case convert function.

    """
    # Check "falsy" values
    text = utils.underscore_to_camelcase('')
    assert text == ''
    text = utils.underscore_to_camelcase(False)
    assert text is False

    text = utils.underscore_to_camelcase('test_camel_case_name')
    assert text == 'testCamelCaseName'
    text = utils.underscore_to_camelcase('_test_camel_case_name_End')
    assert text == '_testCamelCaseNameEnd'
    text = utils.underscore_to_camelcase('testCamelCaseName')
    assert text == 'testCamelCaseName'


def test_camelcase_dict():
    """
    Test convertion of dict keys to camel case.

    """
    test_dict = utils.camelcase_dict({
        'a_name': 0,
        'anotherName': 0,
        'Test_name': 0})
    assert 'aName' in test_dict
    assert 'anotherName' in test_dict
    assert 'testName' in test_dict


def test_underscore_dict():
    """
    Test convertion of dict keys to underscore.

    """
    test_dict = utils.underscore_dict({
        'a_name': 0,
        'anotherName': 0,
        'Test_name': 0})
    assert 'a_name' in test_dict
    assert 'another_name' in test_dict
    assert 'test_name' in test_dict


def test_mixedmethod():
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

    assert TestClass.what_am_i() == 'class'
    test_obj = TestClass()
    assert test_obj.what_am_i() == 'instance'


def test_route_path(config):
    """
    Test route URL path generation.

    """
    # TODO: This test should not depend on an API version
    prefix = '/time/api/v1'
    member = 'users'
    pk = '1'
    related = 'tags'

    path = utils.route_path('api.rest.collection', member=member)
    assert path == prefix + '/users/'
    path = utils.route_path('api.rest.member', member=member, pk=pk)
    assert path == prefix + '/users/1/'
    path = utils.route_path(
        'api.rest.related',
        member=member,
        pk=pk,
        related_name=related,
    )
    assert path == (prefix + '/users/1/tags/')


def test_generate_random_hash():
    """
    Test random hash generation function `generate_random_hash`.

    """
    hash = utils.generate_random_hash(salt=u'fdskjgs', hash='sha1')
    assert isinstance(hash, basestring)
    assert len(hash) == 40
    # Invalid hashing algorithms should raise an exception
    with pytest.raises(Exception):
        utils.generate_random_hash(hash='invalid_name')


def test_get_app_namespace():
    """
    Check that function `get_app_namespace` gets proper app namespaces.

    """
    class LocalClass(object):
        pass

    # Check a python module string
    namespace = utils.get_app_namespace('sandglass.app_namespace.module')
    assert namespace == 'app_namespace'
    # Check a sandglass.time module
    namespace = utils.get_app_namespace(utils)
    assert namespace == 'time'
    # Check a class defined in sandglass.time
    namespace = utils.get_app_namespace(utils.mixedmethod)
    assert namespace == 'time'

    # Check non sandglass python module string
    # Non sandglass prefixed modules should raise an exception
    with pytest.raises(Exception):
        utils.get_app_namespace('foreign.namespace.module')

    # Check a non sandglass module
    # Non sandglass prefixed modules should raise an exception
    import os
    with pytest.raises(Exception):
        utils.get_app_namespace(os.path)
