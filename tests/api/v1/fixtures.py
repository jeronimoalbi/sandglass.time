from fixture import DataSet


class GroupData(DataSet):
    """
    User groups data fixture.

    """
    class Manager(object):
        name = u"Managers"
        description = u"Group of managers"

    class Employee(object):
        name = u"Employee"
        description = u"Group of employees"

    class Developer(object):
        name = u"Developer"
        description = u"Group of developers"

    class Other(object):
        name = u"Other"
        description = u"Group of others"


class UserData(DataSet):
    """
    User data fixture.

    """
    class DrWho(object):
        first_name = u"Dr"
        last_name = u"Who"
        email = u"timeywimey@wienfluss.net"
        password = "1234"
        groups = [GroupData.Employee, GroupData.Developer]

    class JamesWilliamElliot(object):
        email = u"humpdydumpdy@wienfluss.net"
        first_name = u"James William"
        last_name = u"Elliot"
        password = "1234"
        groups = [GroupData.Manager]

    class RickCastle(object):
        email = u"ruggedlyhandsome@wienfluss.net"
        first_name = u"Rick"
        last_name = u"Castle"
        password = "1234"
        groups = [GroupData.Developer]

    class TheTardis(object):
        email = u"wibblywobbly@wienfluss.net"
        first_name = u"The"
        last_name = u"Tardis"
        password = "1234"

    class DrJekyll(object):
        email = u"strangecase@wienfluss.net"
        first_name = u"Dr."
        last_name = u"Jekyll"
        password = "1234"

    class ShepherdBook(object):
        email = u"specialhell@serenity.org"
        first_name = u"Shepherd"
        last_name = u"Book"
        password = "1234"


class ClientData(DataSet):
    """
    Client data fixture.

    """
    class SherlockHolmes(object):
        name = u'Sherlock Holmes'

    class MycroftHolmes(object):
        name = u'Mycroft Holmes'

    class JohnWatson(object):
        name = u'Dr. John Watson'

    class GregLestrade(object):
        name = u'DI Greg Lestrade'

    class JamesMoriarty(object):
        name = u'James Moriarty'

    class CharlesMagnussen(object):
        name = u'Charles Augustus Magnussen'


class ProjectData(DataSet):
    """
    Project data fixture.

    """
    class BaskervilleHound(object):
        id = 1
        name = u"The Hound Of Baskerville"
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook

    class PublicProject(object):
        id = 2
        name = u"The Public Project"
        is_public = True
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook
        groups = [GroupData.Employee, GroupData.Developer, GroupData.Other]

    class GrouplessPublicProject(object):
        id = 3
        name = u"The Groupless Public Project"
        is_public = True
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook

    class PrivateProject(object):
        id = 4
        name = u"The Private Project"
        is_public = False
        client = ClientData.MycroftHolmes
        user = UserData.ShepherdBook
        groups = [GroupData.Manager]


class TaskData(DataSet):
    """
    Task data fixture.

    """
    class Backend(object):
        name = u"Backend"
        project = ProjectData.PublicProject
        user = UserData.ShepherdBook

    class Templating(object):
        name = u"Templating"
        user = UserData.ShepherdBook

    Templating.parent = Backend
    Templating.project = Templating.parent.project

    class Meeting(object):
        name = u"Meeting"
        project = ProjectData.PublicProject
        user = UserData.ShepherdBook

    class PrivateTask(object):
        name = u"Task for a private project"
        project = ProjectData.PrivateProject
        user = UserData.ShepherdBook
