from django.conf.urls import url, include
from django.contrib import admin

import oauth2_provider.views
import allauth.account.views

from sso.user.views import (
    LogoutView,
    LoginView,
    ConfirmEmailView,
    PasswordResetFromKeyView,
)
from sso.healthcheck.views import HealthCheckAPIView
from sso.oauth2.views_user import UserRetrieveAPIView
from sso.api.views_user import SessionUserAPIView


admin.autodiscover()


allauth_urlpatterns = [
    url(
        r"^signup/$",
        allauth.account.views.signup,
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
        r"^password/change/$",
        allauth.account.views.password_change,
        name="account_change_password"
    ),
    url(
        r"^password/set/$",
        allauth.account.views.password_set,
        name="account_set_password"
    ),

    url(
        r"^inactive/$",
        allauth.account.views.account_inactive,
        name="account_inactive"
    ),

    url(
        r"^email/$",
        allauth.account.views.email,
        name="account_email"
    ),
    url(
        r"^confirm-email/$",
        allauth.account.views.email_verification_sent,
        name="account_email_verification_sent"
    ),
    url(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        ConfirmEmailView.as_view(),
        name="account_confirm_email"
    ),

    url(
        r"^password/reset/$",
        allauth.account.views.password_reset,
        name="account_reset_password"
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

    # oauth2 application management views
    url(
        r'^applications/$',
        oauth2_provider.views.ApplicationList.as_view(),
        name="list"
    ),
    url(
        r'^applications/register/$',
        oauth2_provider.views.ApplicationRegistration.as_view(),
        name="register"
    ),
    url(
        r'^applications/(?P<pk>\d+)/$',
        oauth2_provider.views.ApplicationDetail.as_view(),
        name="detail"
    ),
    url(
        r'^applications/(?P<pk>\d+)/delete/$',
        oauth2_provider.views.ApplicationDelete.as_view(),
        name="delete"
    ),
    url(
        r'^applications/(?P<pk>\d+)/update/$',
        oauth2_provider.views.ApplicationUpdate.as_view(),
        name="update"
    ),
    url(
        r'^authorized_tokens/$',
        oauth2_provider.views.AuthorizedTokensListView.as_view(),
        name="authorized-token-list"
    ),
    url(
        r'^authorized_tokens/(?P<pk>\d+)/delete/$',
        oauth2_provider.views.AuthorizedTokenDeleteView.as_view(),
        name="authorized-token-delete"
    ),
]

api_urlpatterns = [
    url(
        r'^$',
        HealthCheckAPIView.as_view(),
        name='health-check'
    ),
    url(
        r'^session-user/$',
        SessionUserAPIView.as_view(),
        name='session-user'
    ),
]


urlpatterns = [
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
