from django.test import Client

import pytest


@pytest.mark.django_db
def test_public_views():
    client = Client()
    for view in ('login', 'signup'):
        response = client.get('/accounts/{}/'.format(view))
        assert response.status_code == 200
