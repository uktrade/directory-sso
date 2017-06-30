import pytest

from django.db import connection
from django.db.migrations.executor import MigrationExecutor

from sso.user.tests.factories import UserFactory


@pytest.fixture()
def migration(transactional_db):
    """
    This fixture returns a helper object to test Django data migrations.
    The fixture returns an object with two methods;
     - `before` to initialize db to the state before the migration under test
     - `after` to execute the migration and bring db to the state after the
    migration. The methods return `old_apps` and `new_apps` respectively; these
    can be used to initiate the ORM models as in the migrations themselves.
    For example:
        def test_foo_set_to_bar(migration):
            old_apps = migration.before('my_app', '0001_inital')
            Foo = old_apps.get_model('my_app', 'foo')
            Foo.objects.create(bar=False)
            assert Foo.objects.count() == 1
            assert Foo.objects.filter(bar=False).count() == Foo.objects.count()
            # executing migration
            new_apps = migration.apply('my_app', '0002_set_foo_bar')
            Foo = new_apps.get_model('my_app', 'foo')
            assert Foo.objects.filter(bar=False).count() == 0
            assert Foo.objects.filter(bar=True).count() == Foo.objects.count()
    From: https://gist.github.com/asfaltboy/b3e6f9b5d95af8ba2cc46f2ba6eae5e2
    """
    class Migrator(object):
        def before(self, app, migrate_from, ):
            """ Specify app and starting migration name as in:
                before('app', '0001_before') => app/migrations/0001_before.py
            """
            self.app = app
            self.migrate_from = [(app, migrate_from)]
            self.executor = MigrationExecutor(connection)
            self.executor.migrate(self.migrate_from)
            self._old_apps = self.executor.loader.project_state(
                self.migrate_from).apps
            return self._old_apps

        def apply(self, app, migrate_to):
            """ Migrate forwards to the "migrate_to" migration """
            self.migrate_to = [(app, migrate_to)]
            self.executor.loader.build_graph()  # reload.
            self.executor.migrate(self.migrate_to)
            self._new_apps = self.executor.loader.project_state(
                self.migrate_to).apps
            return self._new_apps

    return Migrator()


@pytest.mark.django_db
def test_user_email_lowercase(migration):
    app = 'user'
    model_name = 'user'
    name = '0004_user_utm'
    migration.before(app, name).get_model(app, model_name)
    user_one = UserFactory.create(
        email='Foo@bar.com'
    )
    user_two = UserFactory.create(
        email='TeSt@HELlo.com'
    )
    migration.apply('user', '0005_auto_20170630_1030')

    for user in [user_one, user_two]:
        user.refresh_from_db()

    assert user_one.email == 'foo@bar.com'
    assert user_two.email == 'test@hello.com'
