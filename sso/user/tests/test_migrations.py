import pytest

from sso.user.tests.factories import UserFactory


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
