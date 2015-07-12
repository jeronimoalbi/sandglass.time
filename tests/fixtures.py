from mixer.backend.sqlalchemy import mixer

from sandglass.time.models.client import Client
from sandglass.time.models.group import Group
from sandglass.time.models.project import Project
from sandglass.time.models.task import Task
from sandglass.time.models.user import User


@mixer.middleware('sandglass.time.models.user.User')
def user_password_middleware(user):
    """
    Sets same user password for all users.

    Password = test.

    """
    user.set_password('test')
    return user


def attach(data, session):
    """
    Add all data objects to a database session.

    """
    instances = []
    for name in dir(data):
        if name.startswith('_'):
            continue

        instance = getattr(data, name)
        session.add(instance)
        instances.append(instance)

    return data


def create_clients(blend, session):
    class ClientData:
        client1 = blend(
            Client,
            name=u'Sherlock Holmes',
        )

        client2 = blend(
            Client,
            name=u'Mycroft Holmes',
        )

        client3 = blend(
            Client,
            name=u'Dr. John Watson',
        )

        client4 = blend(
            Client,
            name=u'DI Greg Lestrade',
        )

        client5 = blend(
            Client,
            name=u'James Moriarty',
        )

        client6 = blend(
            Client,
            name=u'Charles Augustus Magnussen',
        )

    return attach(ClientData, session)


def create_groups(blend, session):
    class GroupData:
        manager = blend(
            Group,
            name=u"Managers",
            description=u"Group of managers",
        )
        employee = blend(
            Group,
            name=u"Employee",
            description=u"Group of employees",
        )
        developer = blend(
            Group,
            name=u"Developer",
            description=u"Group of developers",
        )
        other = blend(
            Group,
            name=u"Other",
            description=u"Group of others",
        )

    return attach(GroupData, session)


def create_users(blend, session):
    groups_query = Group.query(session=session)

    class UserData:
        dr_who = blend(
            User,
            first_name=u"Dr",
            last_name=u"Who",
            email=u"timeywimey@wienfluss.net",
            password="1234",
        )
        dr_who.groups.extend(
            groups_query.filter(
                Group.name.in_([u"Employee", u"Developer"])
            ).all()
        )

        james_william_elliot = blend(
            User,
            email=u"humpdydumpdy@wienfluss.net",
            first_name=u"James William",
            last_name=u"Elliot",
            password="1234",
        )
        james_william_elliot.groups.extend(
            groups_query.filter(Group.name == u"Managers").all()
        )

        rick_castle = blend(
            User,
            email=u"ruggedlyhandsome@wienfluss.net",
            first_name=u"Rick",
            last_name=u"Castle",
            password="1234",
        )
        rick_castle.groups.extend(
            groups_query.filter(Group.name == u"Developer").all()
        )

        the_tardis = blend(
            User,
            email=u"wibblywobbly@wienfluss.net",
            first_name=u"The",
            last_name=u"Tardis",
            password="1234",
        )

        dr_jeckyll = blend(
            User,
            email=u"strangecase@wienfluss.net",
            first_name=u"Dr.",
            last_name=u"Jekyll",
            password="1234",
        )

        shepherd_book = blend(
            User,
            email=u"specialhell@serenity.org",
            first_name=u"Shepherd",
            last_name=u"Book",
            password="1234",
        )

    return attach(UserData, session)


def create_projects(blend, session):
    groups_query = Group.query(session=session)

    class ProjectData:
        baskerville_hound = blend(
            Project,
            name=u"The Hound Of Baskerville",
            client=mixer.SELECT(Client.name == u'Mycroft Holmes'),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )

        public_project = blend(
            Project,
            name=u"The Public Project",
            is_public=True,
            client=mixer.SELECT(Client.name == u'Mycroft Holmes'),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )
        public_project.groups = groups_query.filter(
            Group.name.in_([u"Employee", u"Developer", u"Other"])
        ).all()

        groupless_public_project = blend(
            Project,
            name=u"The Groupless Public Project",
            is_public=True,
            client=mixer.SELECT(Client.name == u'Mycroft Holmes'),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )

        private_project = blend(
            Project,
            name=u"The Private Project",
            is_public=False,
            client=mixer.SELECT(Client.name == u'Mycroft Holmes'),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )
        private_project.groups.extend(
            groups_query.filter(Group.name.in_([u"Manager"])).all()
        )

    return attach(ProjectData, session)


def create_tasks(blend, session):
    class TaskData:
        backend = blend(
            Task,
            name=u"Backend",
            project=mixer.SELECT(Project.name == u"The Public Project"),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )

        templating = blend(
            Task,
            name=u"Templating",
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
            parent=backend,
            project=backend.project,
        )

        meeting = blend(
            Task,
            name=u"Meeting",
            project=mixer.SELECT(Project.name == u"The Public Project"),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )

        private = blend(
            Task,
            name=u"Task for a private project",
            project=mixer.SELECT(Project.name == u"The Private Project"),
            user=mixer.SELECT(User.email == u"specialhell@serenity.org"),
        )

    return attach(TaskData, session)


def create_data(mixer, session):
    class Data:
        clients = create_clients(mixer.blend, session)
        groups = create_groups(mixer.blend, session)
        users = create_users(mixer.blend, session)
        projects = create_projects(mixer.blend, session)
        tasks = create_tasks(mixer.blend, session)

    return Data
