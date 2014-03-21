from .utils import REQUEST_METHODS


def add_action_info(func, name=None, type='*', permission=None, methods=None,
                    extra=None):
    """
    Add API action info to a method.

    """
    if type not in ('*', 'member', 'collection'):
        raise Exception("Invalid resource action type %s" % type)

    # Save action related info
    func.__action__ = {
        'request_method': methods or REQUEST_METHODS,
        'attr_name': func.__name__,
        'name': name or func.__name__.replace('_', '-'),
        'permission': permission,
        'type': type,
        'extra': extra,
    }

    return func


def member_action(name=None, permission=None, methods=None):
    """
    Mark decorated method to be accesible as an action.

    #TODO: Document arguments.

    """
    def inner_member_action(func):
        return add_action_info(func, name=name, type='member',
                               permission=permission, methods=methods)

    return inner_member_action


def collection_action(name=None, permission=None, methods=None):
    """
    Mark decorated method to be accesible as an action.

    #TODO: Document arguments.

    """
    def inner_collection_action(func):
        return add_action_info(func, name=name, type='collection',
                               permission=permission, methods=methods)

    return inner_collection_action


def action(name=None, permission=None, methods=None):
    """
    Mark decorated method to be accesible as an action.

    #TODO: Document arguments.

    """
    def inner_action(func):
        return add_action_info(func, name=name, permission=permission,
                               methods=methods)

    return inner_action
