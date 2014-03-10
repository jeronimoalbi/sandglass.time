from fixture import DataSet

from sandglass.time.tests import BaseFixture


class GroupData(DataSet):
    """
    User groups data fixture.

    """
    class Manager(BaseFixture):
        name = u"Managers"
        description = u"Group of managers"

    class Employee(BaseFixture):
        name = u"Employee"
        description = u"Group of employees"

    class Developer(BaseFixture):
        name = u"Developer"
        description = u"Group of dvelopers"


class UserData(DataSet):
    """
    User data fixture.

    """
    class DrWho(BaseFixture):
        first_name = u"Dr"
        last_name = u"Who"
        email = u"timeywimey@wienfluss.net"
        password = "1234"
        groups = [GroupData.Employee, GroupData.Developer]

    class JamesWilliamElliot(BaseFixture):
        email = u"humpdydumpdy@wienfluss.net"
        first_name = u"James William"
        last_name = u"Elliot"
        password = "1234"
        groups = [GroupData.Manager]

    class RickCastle(BaseFixture):
        email = u"ruggedlyhandsome@wienfluss.net"
        first_name = u"Rick"
        last_name = u"Castle"
        password = "1234"
        groups = [GroupData.Developer]

    class TheTardis(BaseFixture):
        email = u"wibblywobbly@wienfluss.net"
        first_name = u"The"
        last_name = u"Tardis"
        password = "1234"

    class DrJekyll(BaseFixture):
        email = u"strangecase@wienfluss.net"
        first_name = u"Dr."
        last_name = u"Jekyll"
        password = "1234"

    class ShepherdBook(BaseFixture):
        email = u"specialhell@serenity.org"
        first_name = u"Shepherd"
        last_name = u"Book"
        password = "1234"


class ClientData(DataSet):
    """
    Client data fixture.

    """
    class SherlockHolmes(BaseFixture):
        name = u'Sherlock Holmes'

    class MycroftHolmes(BaseFixture):
        name = u'Mycroft Holmes'

    class JohnWatson(BaseFixture):
        name = u'Dr. John Watson'

    class GregLestrade(BaseFixture):
        name = u'DI Greg Lestrade'

    class JamesMoriarty(BaseFixture):
        name = u'James Moriarty'

    class CharlesMagnussen(BaseFixture):
        name = u'Charles Augustus Magnussen'


class ProjectData(DataSet):
    """
    Project data fixture.

    """
    class BaskervilleHound(BaseFixture):
        name = u"The Hound Of Baskerville"
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook

    class PublicProject(BaseFixture):
        name = u"The Public Project"
        is_public = True
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook
        groups = [GroupData.Employee, GroupData.Developer]

    class PrivateProject(BaseFixture):
        name = u"The Private Project"
        is_public = False
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook
        groups = [GroupData.Manager]


class TaskData(DataSet):
    """
    Task data fixture.

    """
    class Backend(BaseFixture):
        name = u"Backend"
        project = ProjectData.PublicProject
        user = UserData.ShepherdBook

    class Templating(BaseFixture):
        name = u"Templating"
        user = UserData.ShepherdBook

    Templating.parent = Backend
    Templating.project = Templating.parent.project

    class Meeting(BaseFixture):
        name = u"Meeting"
        project = ProjectData.PublicProject
        user = UserData.ShepherdBook

    class PrivateTask(BaseFixture):
        name = u"Task for a private project"
        project = ProjectData.PrivateProject
        user = UserData.ShepherdBook
