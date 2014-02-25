# pylint: disable=C0103

from fixture import DataSet

from sandglass.time.tests import BaseFixture

class ClientUserData(DataSet):

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

class ClientClientData(DataSet):

    class irene_adler(BaseFixture):
        name = 'Irene Adler'

    class violet_hunter(BaseFixture):
        name = 'Violet Hunter'