class BaseAPIResource(object):
    """
    Base class for Sandglass time API resources.

    """
    def __init__(self, request):
        self.request = request
