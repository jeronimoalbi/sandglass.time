from fixture import DataSet


class UserData(DataSet):

    class dr_who:
        first_name = "Dr"
        last_name = "Who"
        email = "timeywimey@wienfluss.net"

    class james_william_elliot:
        email = "humpdydumpdy@wienfluss.net"
        first_name = "James William"
        last_name = "Elliot"

    class rick_castle:
        email = "ruggedlyhandsome@wienfluss.net"
        first_name = "Rick"
        last_name = "Castle"

    class the_tardis:
        email = "wibblywobbly@wienfluss.net"
        first_name = "The"
        last_name = "Tardis"

    class dr_jekyll:
        email = "strangecase@wienfluss.net"
        first_name = "Dr."
        last_name = "Jekyll"

    class shepherd_book:
        email = "specialhell@serenity.org"
        first_name = "Shepherd"
        last_name = "Book"


class ClientData(DataSet):

    class sherlock_holmes:
        name = 'Sherlock Holmes'

    class mycroft_holmes:
        name = 'Mycroft Holmes'

    class john_watson:
        name = 'Dr. John Watson'

    class greg_lestrade:
        name = 'DI Greg Lestrade'

    class james_moriarty:
        name = 'James Moriarty'

    class charles_magnussen:
        name = 'Charles Augustus Magnussen'

class ProjectData(DataSet):

    class baskerville_hound:
        name = "The Hound Of Baskerville"
        client = ClientData.mycroft_holmes
        user = UserData.shepherd_book