# pylint: disable=C0103

from fixture import DataSet

from sandglass.time.tests import BaseFixture


class ClientUserData(DataSet):
    # TODO add token, key and salt, move to it's own AuthenticationUser fixture,
    # replace signup/signin process in __init__ 
    class testuser(BaseFixture):
        first_name = u"test"
        last_name = u"user"
        email = u"testuser@wienfluss.net"
        password = "1234"

    class dr_schiwago(BaseFixture):
        first_name = u"Dr. Jurij"
        last_name = u"Schiwago"
        email = u"omarsharif@wienfluss.net"
        password = "1234"

    class humphrey_bogart(BaseFixture):
        first_name = u"Richard"
        last_name = u"Blaine"
        email = u"humphreybogart@wienfluss.net"
        password = "1234"

    class max_adler(BaseFixture):
        first_name = u"Max"
        last_name = u"Adler"
        email = u"heldenintirol@wienfluss.net"
        password = "1234"
