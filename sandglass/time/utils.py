import re

CAMELCASE_RE = re.compile('(.)([A-Z]{1})')


def camelcase_to_underscore(name):
    """
    Convert camel case names to underscore.

    Return a String.

    """
    return CAMELCASE_RE.sub(r'\1_\2', name).lower()
