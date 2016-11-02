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
    assert '?next=' not in html
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


def test_password_reset_email_with_valid_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['ilovecats.com']
    request = rf.get('/')
    request.GET = {'next': 'http://ilovecats.com/cats/'}
    context = {
        'password_reset_url': 'http://reset.com',
        'request': request,
    }

    html = render_to_string(
        'account/email/password_reset_key_message.html',
        context
    )

    assert 'http://reset.com?next=http://ilovecats.com/cats/' in html


def test_password_reset_email_with_invalid_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com']
    request = rf.get('/')
    request.GET = {'next': 'http://ilovecats.com/cats/'}
    context = {
        'password_reset_url': 'http://reset.com',
        'request': request,
    }

    html = render_to_string(
        'account/email/password_reset_key_message.html',
        context
    )

    assert 'http://reset.com?next=http://ilovecats.com/cats/' not in html
    assert 'http://reset.com' in html


def test_password_reset_email_with_internal_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['ilovecats.com']
    request = rf.get('/')
    request.GET = {'next': '/next/'}
    context = {
        'password_reset_url': 'http://reset.com',
        'request': request,
    }

    html = render_to_string(
        'account/email/password_reset_key_message.html',
        context
    )

    assert 'http://reset.com?next=/next/' in html


def test_password_reset_email_txt_with_valid_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['ilovecats.com']
    request = rf.get('/')
    request.GET = {'next': 'http://ilovecats.com/cats/'}
    context = {
        'password_reset_url': 'http://reset.com',
        'request': request,
    }

    txt = render_to_string(
        'account/email/password_reset_key_message.txt',
        context
    )

    assert 'http://reset.com?next=http://ilovecats.com/cats/' in txt


def test_password_reset_email_txt_with_invalid_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['example.com']
    request = rf.get('/')
    request.GET = {'next': 'http://ilovecats.com/cats/'}
    context = {
        'password_reset_url': 'http://reset.com',
        'request': request,
    }

    txt = render_to_string(
        'account/email/password_reset_key_message.txt',
        context
    )

    assert 'http://reset.com?next=http://ilovecats.com/cats/' not in txt
    assert 'http://reset.com' in txt


def test_password_reset_email_txt_with_internal_next_param(rf, settings):
    settings.ALLOWED_REDIRECT_DOMAINS = ['ilovecats.com']
    request = rf.get('/')
    request.GET = {'next': '/next/'}
    context = {
        'password_reset_url': 'http://reset.com',
        'request': request,
    }

    txt = render_to_string(
        'account/email/password_reset_key_message.txt',
        context
    )

    assert 'http://reset.com?next=/next/' in txt


def test_confirmation_email():
    context = {
        'activate_url': 'http://confirm.com'
    }
    html = render_to_string(
        'account/email/email_confirmation_message.html', context
    )
    assert 'http://confirm.com' in html
    assert 'Verify your email address' in html
