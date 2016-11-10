from django.template.loader import render_to_string
from django.core.urlresolvers import reverse


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


def test_next_param_in_form_action_on_login_page(rf):
    # So must redirect to next when form is invalid as well
    request = rf.get('/')
    request.GET = {'next': 'https://next'}

    html = render_to_string('account/login.html', {'request': request})

    url = reverse('account_login') + '?next=https://next'
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_not_in_form_action_on_login_page_next_unspecified(rf):
    request = rf.get('/')
    request.GET = {}

    html = render_to_string('account/login.html', {'request': request})

    url = reverse('account_login')
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_in_form_action_on_logout_page(rf):
    # So must redirect to next when form is invalid as well
    request = rf.get('/')
    request.GET = {'next': 'https://next'}

    html = render_to_string('account/logout.html', {'request': request})

    url = reverse('account_logout') + '?next=https://next'
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_not_in_form_action_on_logout_page_next_unspecified(rf):
    request = rf.get('/')
    request.GET = {}

    html = render_to_string('account/logout.html', {'request': request})

    url = reverse('account_logout')
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_in_form_action_on_signup_page(rf):
    # So must redirect to next when form is invalid as well
    request = rf.get('/')
    request.GET = {'next': 'https://next'}

    html = render_to_string('account/signup.html', {'request': request})

    url = reverse('account_signup') + '?next=https://next'
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_not_in_form_action_on_signup_page_next_unspecified(rf):
    request = rf.get('/')
    request.GET = {}

    html = render_to_string('account/signup.html', {'request': request})

    url = reverse('account_signup')
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_in_form_action_on_password_change_page(rf):
    # So must redirect to next when form is invalid as well
    request = rf.get('/')
    request.GET = {'next': 'https://next'}

    html = render_to_string('account/password_change.html',
                            {'request': request})

    url = reverse('account_change_password') + '?next=https://next'
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_not_in_action_on_psswd_change_page_next_unspecified(rf):
    request = rf.get('/')
    request.GET = {}

    html = render_to_string('account/password_change.html',
                            {'request': request})

    url = reverse('account_change_password')
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_in_form_action_on_password_reset_page(rf):
    # So must redirect to next when form is invalid as well
    request = rf.get('/')
    request.GET = {'next': 'https://next'}

    html = render_to_string('account/password_reset.html',
                            {'request': request})

    url = reverse('account_reset_password') + '?next=https://next'
    assert 'action="{url}"'.format(url=url) in html


def test_next_param_not_in_action_on_psswd_reset_page_next_unspecified(rf):
    request = rf.get('/')
    request.GET = {}

    html = render_to_string('account/password_reset.html',
                            {'request': request})

    url = reverse('account_reset_password')
    assert 'action="{url}"'.format(url=url) in html


def test_google_tag_manager():
    expected_head = render_to_string('google_tag_manager_head.html')
    expected_body = render_to_string('google_tag_manager_body.html')

    html = render_to_string('base.html')

    assert expected_head in html
    assert expected_body in html
    # sanity check
    assert 'www.googletagmanager.com' in expected_head
    assert 'www.googletagmanager.com' in expected_body
