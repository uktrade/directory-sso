from unittest import TestCase

import pytest

from django.test import Client
from django.core.urlresolvers import reverse

from sso.user.models import User


@pytest.mark.django_db
class DownloadCaseStudyCSVTestCase(TestCase):

    header = (
        'created,date_joined,email,id,is_active,is_staff,is_superuser,'
        'last_login,modified,oauth2_provider_application'
    )

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(self.superuser)

    def test_download_csv_single_user(self):
        data = {
            'action': 'download_csv',
            '_selected_action': User.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:user_user_changelist'),
            data,
            follow=True
        )

        row_one = (
            "{created},{date_joined},admin@example.com,{id},True,True,True,"
            "{last_login},{modified},"
        ).format(
            created=self.superuser.created,
            date_joined=self.superuser.date_joined,
            id=self.superuser.id,
            last_login=self.superuser.last_login,
            modified=self.superuser.modified,
        )
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.header
        assert actual[1] == row_one

    def test_download_csv_multiple_multiple_users(self):

        for x in range(2):
            User.objects.create(email=x)

        data = {
            'action': 'download_csv',
            '_selected_action': User.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:user_user_changelist'),
            data,
            follow=True
        )

        user_one = User.objects.all()[2]
        row_one = (
            '{created},{date_joined},{email},{id},{is_active},{is_staff},'
            '{is_superuser},,{modified},'
        ).format(
            created=user_one.created,
            date_joined=user_one.date_joined,
            email=user_one.email,
            id=user_one.id,
            is_active=user_one.is_active,
            is_staff=user_one.is_staff,
            is_superuser=user_one.is_superuser,
            modified=user_one.modified,
        )

        user_two = User.objects.all()[1]
        row_two = (
            '{created},{date_joined},{email},{id},{is_active},{is_staff},'
            '{is_superuser},,{modified},'
        ).format(
            created=user_two.created,
            date_joined=user_two.date_joined,
            email=user_two.email,
            id=user_two.id,
            is_active=user_two.is_active,
            is_staff=user_two.is_staff,
            is_superuser=user_two.is_superuser,
            modified=user_two.modified,
        )

        user_three = User.objects.all()[0]
        row_three = (
            '{created},{date_joined},{email},{id},{is_active},{is_staff},'
            '{is_superuser},{last_login},{modified},'
        ).format(
            created=user_three.created,
            date_joined=user_three.date_joined,
            email=user_three.email,
            id=user_three.id,
            is_active=user_three.is_active,
            is_staff=user_three.is_staff,
            is_superuser=user_three.is_superuser,
            last_login=user_three.last_login,
            modified=user_three.modified,
        )

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.header
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three
