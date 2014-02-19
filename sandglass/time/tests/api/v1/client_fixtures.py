from fixture import DataSet
from sandglass.time.tests.fixtures import BaseFixture

class ClientUserData(DataSet):

    class testuser(BaseFixture):
        first_name = "test"
        last_name = "user"
        email = "testuser@wienfluss.net"
        password = "1234"

    class dr_schiwago(BaseFixture):
        first_name = "Dr. Jurij"
        last_name = "Schiwago"
        email = "omarsharif@wienfluss.net"
        password = "1234"

    class humphrey_bogart(BaseFixture):
        first_name = "Richard"
        last_name = "Blaine"
        email = "humphreybogart@wienfluss.net"
        password = "1234"

    class max_adler(BaseFixture):
        first_name = "Max"
        last_name = "Adler"
        email = "heldenintirol@wienfluss.net"
        password = "1234"

