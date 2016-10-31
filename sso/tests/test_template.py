from django.template.loader import render_to_string


def test_password_reset_email():
    context = {
        'password_reset_url': 'http://reset.com',
    }
    html = render_to_string(
        'account/email/password_reset_key_message.html',
        context
    )
    assert 'http://reset.com' in html
    assert 'Reset password' in html


def test_confirmation_email():
    context = {
        'activate_url': 'http://confirm.com'
    }
    html = render_to_string(
        'account/email/email_confirmation_message.html', context
    )
    assert 'http://confirm.com' in html
    assert 'Verify your email address' in html
