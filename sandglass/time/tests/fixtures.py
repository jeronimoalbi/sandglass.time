from fixture import DataSet
import inspect


class BaseFixture():

    """
    Base class with util functions for fixtures
    """
    @classmethod
    def json_data(cls):
        """
        Returns clean attributes only of fixture class
        """
        attr = {}
        for name in dir(cls):
            value = getattr(cls, name)
            if (not name.startswith('__') and
                not inspect.ismethod(value) and
                not name == '_dataset' and 
                not name == 'ref'):
                    attr[name] = value
        return attr

class UserData(DataSet):

    class dr_who(BaseFixture):
        first_name = "Dr"
        last_name = "Who"
        email = "timeywimey@wienfluss.net"
        password = "1234"

    class james_william_elliot(BaseFixture):
        email = "humpdydumpdy@wienfluss.net"
        first_name = "James William"
        last_name = "Elliot"
        password = "1234"

    class rick_castle(BaseFixture):
        email = "ruggedlyhandsome@wienfluss.net"
        first_name = "Rick"
        last_name = "Castle"
        password = "1234"

    class the_tardis(BaseFixture):
        email = "wibblywobbly@wienfluss.net"
        first_name = "The"
        last_name = "Tardis"
        password = "1234"

    class dr_jekyll(BaseFixture):
        email = "strangecase@wienfluss.net"
        first_name = "Dr."
        last_name = "Jekyll"
        password = "1234"

    class shepherd_book(BaseFixture):
        email = "specialhell@serenity.org"
        first_name = "Shepherd"
        last_name = "Book"
        password = "1234"


class ClientData(DataSet):

    class sherlock_holmes(BaseFixture):
        name = 'Sherlock Holmes'

    class mycroft_holmes(BaseFixture):
        name = 'Mycroft Holmes'

    class john_watson(BaseFixture):
        name = 'Dr. John Watson'

    class greg_lestrade(BaseFixture):
        name = 'DI Greg Lestrade'

    class james_moriarty(BaseFixture):
        name = 'James Moriarty'

    class charles_magnussen(BaseFixture):
        name = 'Charles Augustus Magnussen'


class ProjectData(DataSet):

    class baskerville_hound(BaseFixture):
        name = "The Hound Of Baskerville"
        client = ClientData.mycroft_holmes
        user = UserData.shepherd_book
