from collections import OrderedDict
from datetime import timedelta
from unittest import TestCase
from unittest.mock import patch

import pytest
from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.admin import site
from django.test import Client
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time

from core.tests.test_helpers import reload_urlconf
from sso.oauth2.tests.factories import AccessTokenFactory, ApplicationFactory
from sso.user import admin
from sso.user.models import User
from sso.user.tests.factories import UserFactory


@pytest.mark.django_db
class DownloadCaseStudyCSVTestCase(TestCase):

    header = (
        'created,date_joined,email,first_name,hashed_uuid,'
        'id,is_active,is_staff,is_superuser,'
        'last_login,last_name,lessoncompleted,modified,oauth2_provider_application,page_views,user_profile,'
        'utm,verification_code'
    )

    def setUp(self):
        self.superuser = User.objects.create_superuser(email='admin@example.com', password='test')
        self.client = Client()
        self.client.force_login(self.superuser)

    def test_download_csv_single_user(self):
        data = {'action': 'download_csv', '_selected_action': User.objects.all().values_list('pk', flat=True)}

        response = self.client.post(reverse('admin:user_user_changelist'), data, follow=True)

        user = User.objects.first()
        row_one = (
            "{created},{date_joined},admin@example.com,,{hashed_uuid},"
            "{id},True,True,True,"
            "{last_login},,,{modified},,,,,{utm},"
        ).format(
            created=user.created,
            date_joined=user.date_joined,
            hashed_uuid=user.hashed_uuid,
            id=user.id,
            last_login=user.last_login,
            modified=user.modified,
            utm=user.utm,
        )
        actual = str(response.content, 'utf-8').split('\r\n')
        assert actual[0] == self.header
        assert actual[1] == row_one

    def test_download_csv_multiple_multiple_users(self):

        for x in range(2):
            User.objects.create(email=x)

        data = {'action': 'download_csv', '_selected_action': User.objects.all().values_list('pk', flat=True)}
        response = self.client.post(reverse('admin:user_user_changelist'), data, follow=True)

        user_one = User.objects.all()[2]
        row_one = (
            '{created},{date_joined},{email},,{hashed_uuid},'
            '{id},{is_active},{is_staff},'
            '{is_superuser},,,,{modified},,,{user_profile},'
            '{utm},'
            '{verification_code}'
        ).format(
            created=user_one.created,
            date_joined=user_one.date_joined,
            email=user_one.email,
            hashed_uuid=user_one.hashed_uuid,
            id=user_one.id,
            is_active=user_one.is_active,
            is_staff=user_one.is_staff,
            is_superuser=user_one.is_superuser,
            modified=user_one.modified,
            user_profile='',
            utm=user_one.utm,
            verification_code='',
        )

        user_two = User.objects.all()[1]
        row_two = (
            '{created},{date_joined},{email},,{hashed_uuid},'
            '{id},{is_active},{is_staff},'
            '{is_superuser},,,,{modified},,,{user_profile},,{utm},'
            '{verification_code}'
        ).format(
            created=user_two.created,
            date_joined=user_two.date_joined,
            email=user_two.email,
            hashed_uuid=user_two.hashed_uuid,
            id=user_two.id,
            is_active=user_two.is_active,
            is_staff=user_two.is_staff,
            is_superuser=user_two.is_superuser,
            modified=user_two.modified,
            user_profile='',
            utm=user_two.utm,
            verification_code='',
        )

        user_three = User.objects.all()[0]
        row_three = (
            '{created},{date_joined},{email},,{hashed_uuid},'
            '{id},{is_active},{is_staff},'
            '{is_superuser},{last_login},,,{modified},,,{user_profile},,{utm},'
            '{verification_code}'
        ).format(
            created=user_three.created,
            date_joined=user_three.date_joined,
            email=user_three.email,
            hashed_uuid=user_three.hashed_uuid,
            id=user_three.id,
            is_active=user_three.is_active,
            is_staff=user_three.is_staff,
            is_superuser=user_three.is_superuser,
            last_login=user_three.last_login,
            modified=user_three.modified,
            user_profile='',
            utm=user_three.utm,
            verification_code='',
        )

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.header
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three


@pytest.fixture
def superuser():
    return User.objects.create_superuser(email='admin@example.com', password='test')


@pytest.fixture
def superuser_client(superuser):
    client = Client()
    client.force_login(superuser)
    return client


@pytest.mark.django_db
@patch('sso.user.admin.UserAdmin.get_fab_user_ids')
def test_download_csv_exops_not_fab(mock_get_fab_user_ids, settings, superuser_client):

    settings.EXOPS_APPLICATION_CLIENT_ID = 'debug'
    application = ApplicationFactory(client_id='debug')
    user_one = AccessTokenFactory.create(application=application).user  # should be in the csv
    user_two = AccessTokenFactory.create(application=application).user  # should not be in the csv
    AccessTokenFactory.create().user  # should not be in the csv

    mock_get_fab_user_ids.return_value = [user_two.pk]
    data = {'action': 'download_csv_exops_not_fab', '_selected_action': User.objects.all().values_list('pk', flat=True)}
    response = superuser_client.post(reverse('admin:user_user_changelist'), data, follow=True)

    expected_row = OrderedDict(
        [
            ('created', user_one.created),
            ('date_joined', user_one.date_joined),
            ('email', user_one.email),
            ('first_name', ''),
            ('hashed_uuid', user_one.hashed_uuid),
            ('id', user_one.id),
            ('is_active', user_one.is_active),
            ('is_staff', user_one.is_staff),
            ('is_superuser', user_one.is_superuser),
            ('last_login', user_one.last_login),
            ('last_name', ''),
            ('lessoncompleted', ''),
            ('modified', user_one.modified),
            ('oauth2_provider_application', ''),
            ('page_views', ''),
            ('user_profile', ''),
            ('utm', user_one.utm),
            ('verification_code', ''),
        ]
    )

    actual = str(response.content, 'utf-8').split('\r\n')
    assert actual[0] == ','.join(expected_row.keys())
    assert actual[1] == ','.join(map(str, expected_row.values()))


@pytest.mark.django_db
@patch('sso.user.admin.UserAdmin.get_fab_user_ids')
def test_download_csv_exops_not_fab_distinct(mock_get_fab_user_ids, settings, superuser_client):

    settings.EXOPS_APPLICATION_CLIENT_ID = 'debug'
    application = ApplicationFactory(client_id='debug')
    # given a user has created multiple tokens
    token_one = AccessTokenFactory.create(
        application=application,
    )
    AccessTokenFactory.create(
        application=application,
        user=token_one.user,
    )

    mock_get_fab_user_ids.return_value = []
    data = {'action': 'download_csv_exops_not_fab', '_selected_action': User.objects.all().values_list('pk', flat=True)}
    # when the export csv is created
    response = superuser_client.post(reverse('admin:user_user_changelist'), data, follow=True)

    rows = str(response.content, 'utf-8').strip().split('\r\n')
    # then the user is listed only once, not once per token created
    assert len(rows) == 2  # header and single row


@pytest.mark.django_db
def test_download_password_reset_links(settings, superuser_client):
    UserFactory.create()

    data = {
        'action': 'download_password_reset_links',
        '_selected_action': User.objects.all().values_list('pk', flat=True),
    }
    response = superuser_client.post(reverse('admin:user_user_changelist'), data, follow=True)

    assert '/accounts/password/reset/key/' in str(response.content)


@pytest.mark.django_db
def test_download_email_verification_links(settings, superuser_client):
    user = UserFactory.create()
    EmailAddress(user=user, email=user.email).save()

    data = {
        'action': 'download_email_verification_links',
        '_selected_action': User.objects.all().values_list('pk', flat=True),
    }
    response = superuser_client.post(reverse('admin:user_user_changelist'), data, follow=True)

    assert '/accounts/confirm-email/' in str(response.content)


@pytest.mark.django_db
class CompanyAdminAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    AUTHENTICATION_BACKENDS_CLASSES = (
        'authbroker_client.backends.AuthbrokerBackend',
        'oauth2_provider.backends.OAuth2Backend',
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    )

    @pytest.mark.django_db
    def test_nonsuperuser_cannot_access_user_changelist(self):
        non_admin_user = UserFactory(is_staff=False)
        non_admin_user.save()

        settings.AUTHENTICATION_BACKENDS = self.AUTHENTICATION_BACKENDS_CLASSES
        settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
        reload_urlconf()
        self.client.force_login(non_admin_user)
        url = reverse('admin:user_user_changelist')

        response = self.client.get(url)
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_no_user_cannot_access_user_changelist(self):

        settings.AUTHENTICATION_BACKENDS = self.AUTHENTICATION_BACKENDS_CLASSES
        settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED = True
        reload_urlconf()

        url = reverse('admin:user_user_changelist')

        response = self.client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
def test_GDPR_compliance_filter(rf, superuser):
    three_years_ago = 365 * 3

    with freeze_time(timezone.now() - timedelta(days=three_years_ago + 1)):
        user_one = UserFactory()

    with freeze_time(timezone.now() - timedelta(days=three_years_ago)):
        user_two = UserFactory()

    with freeze_time(timezone.now() - timedelta(days=three_years_ago - 1)):
        user_three = UserFactory()

    modeladmin = admin.UserAdmin(User, site)
    request = rf.get('/', {'gdpr': True})
    request.user = superuser
    changelist = modeladmin.get_changelist_instance(request)
    queryset = changelist.get_queryset(request)

    assert queryset.count() == 2
    assert user_one in queryset
    assert user_two in queryset
    assert user_three not in queryset
