from django.conf.urls import url, include
from django.contrib import admin

import oauth2_provider.views
import allauth.account.views

from config import settings
from sso.user.views import (
    ConfirmEmailView,
    EmailVerificationSentView,
    LoginView,
    LogoutView,
    PasswordResetFromKeyView,
    SSOLandingPage,
    SignupView,
)
from sso.healthcheck.views import (
    DatabaseAPIView, PingAPIView
)
from sso.oauth2.views_user import UserRetrieveAPIView
from sso.api.views_user import (
    SessionUserAPIView, LastLoginAPIView, PasswordCheckAPIView
)
from testapi.views import UserByEmailAPIView

admin.autodiscover()


allauth_urlpatterns = [
    url(
        r"^signup/$",
        SignupView.as_view(),
        name="account_signup"
    ),
    url(
        r"^login/$",
        LoginView.as_view(),
        name="account_login"
    ),
    url(
        r"^logout/$",
        LogoutView.as_view(),
        name="account_logout"
    ),
    url(
        r"^inactive/$",
        allauth.account.views.account_inactive,
        name="account_inactive"
    ),
    url(
        r"^confirm-email/$",
        EmailVerificationSentView.as_view(),
        name="account_email_verification_sent"
    ),
    url(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email"
    ),

    url(
        r"^password/set/$",
        allauth.account.views.password_set,
        name="account_set_password"
    ),
    url(
        r"^password/reset/$",
        allauth.account.views.password_reset,
        name="account_reset_password"
    ),
    url(
        r"^password/change/$",
        allauth.account.views.password_change,
        name="account_change_password"
    ),
    url(
        r"^password/reset/done/$",
        allauth.account.views.password_reset_done,
        name="account_reset_password_done"
    ),
    url(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key"
    ),
]


oauth2_provider_patterns = [
    url(
        r'^user-profile/v1/$',
        UserRetrieveAPIView.as_view(),
        name='user-profile'
    ),
    url(
        r'^authorize/$',
        oauth2_provider.views.AuthorizationView.as_view(),
        name="authorize"
    ),
    url(
        r'^token/$',
        oauth2_provider.views.TokenView.as_view(),
        name="token"
    ),
    url(
        r'^revoke_token/$',
        oauth2_provider.views.RevokeTokenView.as_view(),
        name="revoke-token"
    ),
]

api_urlpatterns = [
    url(
        r'^healthcheck/database/$',
        DatabaseAPIView.as_view(),
        name='health-check-database'
    ),
    url(
        r'^healthcheck/ping/$',
        PingAPIView.as_view(),
        name='health-check-ping'
    ),
    url(
        r'^session-user/$',
        SessionUserAPIView.as_view(),
        name='session-user'
    ),
    url(
        r'^last-login/$',
        LastLoginAPIView.as_view(),
        name='last-login'
    ),
    url(
        r'^password-check/$',
        PasswordCheckAPIView.as_view(),
        name='password-check'
    ),
]


urlpatterns = [
    url(
        r"^$",
        SSOLandingPage.as_view(),
        name="sso_root"),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^accounts/',
        include(allauth_urlpatterns)
    ),
    url(
        r'^oauth2/',
        include(oauth2_provider_patterns, namespace='oauth2_provider')
    ),
    url(
        r'^api/v1/',
        include(api_urlpatterns)
    ),
]

if settings.ENABLE_TEST_API:
    api_urlpatterns += [
        url(
            r'^testapi/',
            include('testapi.urls', namespace='testapi')
        )
    ]
