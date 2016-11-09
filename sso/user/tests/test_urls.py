import http

from django.core.urlresolvers import reverse

from sso import constants


def test_feedback_redirect(client):
    response = client.get(reverse('feedback'), follow=False)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == constants.FEEDBACK_FORM_URL


def test_terms_redirect(client):
    response = client.get(reverse('terms'), follow=False)

    assert response.status_code == http.client.FOUND
    assert response.get('Location') == constants.TERMS_AND_CONDITIONS_URL
