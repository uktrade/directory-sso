from django.test import Client


def test_docs():
    client = Client()
    response = client.get('/docs')
    assert response.status_code == 301
