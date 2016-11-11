from django.template.loader import render_to_string


def test_password_reset_email(rf):
    context = {
        'password_reset_url': 'http://reset.com',
        'request': rf.get('/'),
    }
    html = render_to_string(
        'account/email/password_reset_key_message.html',
        context
    )
    assert 'http://reset.com' in html
    assert 'Reset password' in html


def test_password_reset_email_txt(rf):
    context = {
        'password_reset_url': 'http://reset.com',
        'request': rf.get('/'),
    }
    txt = render_to_string(
        'account/email/password_reset_key_message.txt',
        context
    )
    assert 'http://reset.com' in txt
    assert '?next=' not in txt


def test_confirmation_email():
    context = {
        'activate_url': 'http://confirm.com'
    }
    html = render_to_string(
        'account/email/email_confirmation_message.html', context
    )
    assert 'http://confirm.com' in html
    assert 'Verify your email address' in html


def test_google_tag_manager():
    expected_head = render_to_string('google_tag_manager_head.html')
    expected_body = render_to_string('google_tag_manager_body.html')

    html = render_to_string('base.html')

    assert expected_head in html
    assert expected_body in html
    # sanity check
    assert 'www.googletagmanager.com' in expected_head
    assert 'www.googletagmanager.com' in expected_body
