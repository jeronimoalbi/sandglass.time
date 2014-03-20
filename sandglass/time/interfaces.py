from zope.interface import Interface


class IDescribable(Interface):
    """
    Interface for objects that supports being described.

    Objects that implement this interface are able to give some
    meta information that can be used to describe some of their
    functionality.

    """
    def describe(self):
        """
        Get meta information about current object functionality.

        Returns a DIctionary.

        """
