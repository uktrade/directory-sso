import allauth.account.views
import directory_components.views
import oauth2_provider.views

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap

import conf.sitemaps
import sso.api.views_activity_stream
import sso.api.views_user
import sso.healthcheck.views
import sso.oauth2.views_user
import sso.testapi.views
import sso.user.views

sitemaps = {
    'static': conf.sitemaps.StaticViewSitemap,
}


admin.autodiscover()


allauth_urlpatterns = [
    url(
        r"^signup/$",
        sso.user.views.SignupView.as_view(),
        name="account_signup"
    ),
    url(
        r"^login/$",
        sso.user.views.LoginView.as_view(),
        name="account_login"
    ),
    url(
        r"^logout/$",
        sso.user.views.LogoutView.as_view(),
        name="account_logout"
    ),
    url(
        r"^inactive/$",
        allauth.account.views.account_inactive,
        name="account_inactive"
    ),
    url(
        r"^confirm-email/$",
        allauth.account.views.EmailVerificationSentView.as_view(),
        name="account_email_verification_sent"
    ),
    url(
        r"^confirm-email/(?P<key>[-:\w]+)/$",
        sso.user.views.ConfirmEmailView.as_view(),
        name="account_confirm_email"
    ),

    url(
        r"^password/set/$",
        allauth.account.views.password_set,
        name="account_set_password"
    ),
    url(
        r"^password/reset/$",
        sso.user.views.PasswordResetView.as_view(),
        name="account_reset_password"
    ),
    url(
        r"^password/change/$",
        login_required(sso.user.views.PasswordChangeView.as_view()),
        name="account_change_password"
    ),
    url(
        r"^password/reset/done/$",
        allauth.account.views.password_reset_done,
        name="account_reset_password_done"
    ),
    url(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        sso.user.views.PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key"
    ),
]


oauth2_provider_patterns = [
    url(
        r'^user-profile/v1/$',
        sso.oauth2.views_user.UserRetrieveAPIView.as_view(),
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
        sso.healthcheck.views.DatabaseAPIView.as_view(),
        name='health-check-database'
    ),
    url(
        r'^healthcheck/ping/$',
        sso.healthcheck.views.PingAPIView.as_view(),
        name='health-check-ping'
    ),
    url(
        r'^session-user/$',
        sso.api.views_user.SessionUserAPIView.as_view(),
        name='session-user'
    ),
    url(
        r'^last-login/$',
        sso.api.views_user.LastLoginAPIView.as_view(),
        name='last-login'
    ),
    url(
        r'^password-check/$',
        sso.api.views_user.PasswordCheckAPIView.as_view(),
        name='password-check'
    ),
    url(
        r'^activity-stream/$',
        sso.api.views_activity_stream.ActivityStreamViewSet.as_view(
            {'get': 'list'}
        ),
        name='activity-stream'
    ),
]


urlpatterns = [
    url(
        r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps},
        name='sitemap'
    ),
    url(
        r"^robots\.txt$",
        directory_components.views.RobotsView.as_view(),
        name='robots'
    ),
    url(
        r"^$",
        sso.user.views.SSOLandingPage.as_view(),
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
    url(
        r'^testapi/user-by-email/(?P<email>.*)/$',
        sso.testapi.views.UserByEmailAPIView.as_view(),
        name='user_by_email'
    ),
]
