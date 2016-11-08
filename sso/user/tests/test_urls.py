import http

from django.core.urlresolvers import reverse


def test_feedback_redirect(client, settings):
    response = client.get(reverse('feedback'), follow=False)

    assert settings.FEEDBACK_FORM_URL
    assert response.status_code == http.client.FOUND
    assert response.get('Location') == settings.FEEDBACK_FORM_URL
