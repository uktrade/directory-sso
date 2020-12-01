import http

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_sitemaps_200(client):
    url = reverse('sitemap')

    response = client.get(url)

    assert response.status_code == http.client.OK
