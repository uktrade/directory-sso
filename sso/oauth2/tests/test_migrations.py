import pytest

from sso.oauth2.tests import factories


@pytest.mark.django_db
def test_access_token_related_name_change(migration):
    migration.before('user', '0003_auto_20161130_1138')
    historic_apps = migration.before('oauth2_provider', '0001_initial')

    HistoricAccessTokenFactory = factories.build_historic_access_token_factory(
        historic_apps
    )
    historic_access_token = HistoricAccessTokenFactory.create()
    historic_user = historic_access_token.user

    assert historic_user.accesstoken_set.count() == 1
    assert historic_access_token in historic_user.accesstoken_set.all()

    apps = migration.apply('oauth2_provider', '0005_auto_20170514_1141')

    User = apps.get_model('user', 'User')
    user = User.objects.get(pk=historic_access_token.user.pk)

    AccessToken = apps.get_model('oauth2_provider', 'AccessToken')
    access_token = AccessToken.objects.get(pk=historic_access_token.pk)

    assert user.oauth2_provider_accesstoken.count() == 1
    assert access_token in user.oauth2_provider_accesstoken.all()
