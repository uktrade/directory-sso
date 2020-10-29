from allauth.socialaccount.models import SocialAccount

from sso.user import utils


def test_get_social_account_image_google():
    account = SocialAccount(
        extra_data={
            'id': '123',
            'email': 'jim@example.com',
            'verified_email': True,
            'name': 'Jim Example',
            'given_name': 'Jim',
            'family_name': 'Example',
            'picture': 'https://image.com/image.png',
            'locale': 'en'
        },
        provider='google',
    )

    assert utils.get_social_account_image(account) == 'https://image.com/image.png'


def test_get_social_account_no_image_google():
    account = SocialAccount(
        extra_data={
            'id': '123',
            'email': 'jim@example.com',
            'verified_email': True,
            'name': 'Jim Example',
            'given_name': 'Jim',
            'family_name': 'Example',
            'locale': 'en'
        },
        provider='google',
    )

    assert utils.get_social_account_image(account) is None


def test_get_social_account_image_linkedin():
    account = SocialAccount(
        extra_data={
            'profilePicture': {
                'displayImage~': {
                    'paging': {
                        'count': 10,
                        'start': 0,
                        'links': []
                    },
                    'elements': [
                        {
                            'identifiers': [
                                {
                                  'identifier': 'https://image.com/image.png',
                                }
                            ]
                        },
                    ]
                }
            },
            'id': 's27gBbCPyF'
        },
        provider='linkedin_oauth2',
    )

    assert utils.get_social_account_image(account) == 'https://image.com/image.png'


def test_get_social_account_image_linkedin_no_profile_pic():
    account = SocialAccount(
        extra_data={
            'id': 's27gBbCPyF'
        },
        provider='linkedin_oauth2',
    )

    assert utils.get_social_account_image(account) is None


def test_get_social_account_image_linkedin_no_display_image():
    account = SocialAccount(
        extra_data={
            'profilePicture': {
            },
            'id': 's27gBbCPyF'
        },
        provider='linkedin_oauth2',
    )
    assert utils.get_social_account_image(account) is None


def test_get_social_account_image_linkedin_no_elements():
    account = SocialAccount(
        extra_data={
            'profilePicture': {
                'displayImage~': {
                    'paging': {
                        'count': 10,
                        'start': 0,
                        'links': []
                    },
                    'elements': []
                }
            },
            'id': 's27gBbCPyF'
        },
        provider='linkedin_oauth2',
    )
    assert utils.get_social_account_image(account) is None
