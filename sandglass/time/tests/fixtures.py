# pylint: disable=C0103

from fixture import DataSet

from sandglass.time.tests import BaseFixture


class UserData(DataSet):

    class dr_who(BaseFixture):
        first_name = u"Dr"
        last_name = u"Who"
        email = u"timeywimey@wienfluss.net"
        password = "1234"

    class james_william_elliot(BaseFixture):
        email = u"humpdydumpdy@wienfluss.net"
        first_name = u"James William"
        last_name = u"Elliot"
        password = "1234"

    class rick_castle(BaseFixture):
        email = u"ruggedlyhandsome@wienfluss.net"
        first_name = u"Rick"
        last_name = u"Castle"
        password = "1234"

    class the_tardis(BaseFixture):
        email = u"wibblywobbly@wienfluss.net"
        first_name = u"The"
        last_name = u"Tardis"
        password = "1234"

    class dr_jekyll(BaseFixture):
        email = u"strangecase@wienfluss.net"
        first_name = u"Dr."
        last_name = u"Jekyll"
        password = "1234"

    class shepherd_book(BaseFixture):
        email = u"specialhell@serenity.org"
        first_name = u"Shepherd"
        last_name = u"Book"
        password = "1234"


class ClientData(DataSet):

    class sherlock_holmes(BaseFixture):
        name = u'Sherlock Holmes'

    class mycroft_holmes(BaseFixture):
        name = u'Mycroft Holmes'

    class john_watson(BaseFixture):
        name = u'Dr. John Watson'

    class greg_lestrade(BaseFixture):
        name = u'DI Greg Lestrade'

    class james_moriarty(BaseFixture):
        name = u'James Moriarty'

    class charles_magnussen(BaseFixture):
        name = u'Charles Augustus Magnussen'


class ProjectData(DataSet):

    class baskerville_hound(BaseFixture):
        name = "The Hound Of Baskerville"
        client = ClientData.mycroft_holmes
        user = UserData.shepherd_book
