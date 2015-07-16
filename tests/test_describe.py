from pyramid.testing import DummyRequest

from sandglass.time.api.v1.user import UserResource
from sandglass.time.resource.base import BaseResource


class FooResource(BaseResource):
    name = 'foos'


def test_describe_resource():
    request = DummyRequest()
    resource = FooResource(request)
    describer = resource.describer_cls(resource)
    # Get description from describe and __json__ methods. They are the same.
    for description in [describer.describe(), describer.__json__(request)]:
        assert isinstance(description, dict)
        # Get actions data and check that there are
        # descriptions for member and collection URLs.
        actions = description.get('actions')
        assert actions
        assert 'member' in actions
        assert 'collection' in actions


def test_describe_model_resource():
    request = DummyRequest()
    resource = UserResource(request)
    describer = resource.describer_cls(resource)
    description = describer.describe()
    assert isinstance(description, dict)
    assert 'related' in description
    assert 'schema' in description
    assert 'filters' in description
    # Get actions data and check that there are
    # descriptions for member and collection URLs.
    actions = description.get('actions')
    assert actions
    assert 'member' in actions
    assert 'collection' in actions

    # Check that description is returned when no actions are available.
    # When there are no actions schema can't be described.
    actions = description.pop('actions')
    assert describer.describe_action_schemas(description) == description

    # Check that invalid actions are ignored during schema description
    actions['invalid_name'] = {}
    description['actions'] = actions
    description = describer.describe_action_schemas(description)
    # Invalid action should not be deleted, or changed
    assert description['actions'].get('invalid_name') == {}
