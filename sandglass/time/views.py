""" Cornice services.
"""
import json
from cornice import Service


hello = Service(name='hello', path='/', description="Simplest app")
# TODO: api test service. remove later.
values = Service(name='foo', path='/values/{value}',
                 description="Cornice Demo")

_VALUES = {}

@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'Hello': 'World'}


@values.get()
def get_value(request):
    """Returns the value.
    """
    key = request.matchdict['value']
    return _VALUES.get(key)


@values.post()
def set_value(request):
    """Set the value.

    Returns *True* or *False*.
    """
    key = request.matchdict['value']
    try:
        _VALUES[key] = json.loads(request.body)
    except ValueError:
        return False
    return True
