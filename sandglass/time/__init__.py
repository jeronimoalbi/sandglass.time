VERSION_INFO = {
    'major': 0,
    'minor': 1,
    'micro': 0,
}


def get_version(short=False):
    """
    Concatenates ``VERSION_INFO`` to dotted version string.

    """
    version = "{major!s}.{minor!s}".format(**VERSION_INFO)
    # append micro version only if not short and micro != 0
    if not short and VERSION_INFO['micro']:
        version += ".{micro!s}".format(**VERSION_INFO)

    return version


__version__ = get_version()
