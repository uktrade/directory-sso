import allauth.account.views
import allauth.urls
import allauth.socialaccount
import directory_components.views
import directory_healthcheck.views

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.urls import reverse_lazy
from django.conf import settings

import conf.sitemaps
import sso.api.views_activity_stream
import sso.api.views_user
import sso.oauth2.views_user
import sso.testapi.views
import sso.verification.views
import sso.user.views
import sso.user.views_api


sitemaps = {
    'static': conf.sitemaps.StaticViewSitemap,
}


admin.autodiscover()


allauth_urlpatterns = [
    url(r"^signup/$", sso.user.views.RedirectToProfileSignUp.as_view(), name="account_signup"),
    url(r"^login/$", sso.user.views.LoginView.as_view(), name="account_login"),
    url(r"^logout/$", sso.user.views.LogoutView.as_view(), name="account_logout"),
    url(r"^inactive/$", allauth.account.views.account_inactive, name="account_inactive"),
    url(
        r"^confirm-email/$",
        allauth.account.views.EmailVerificationSentView.as_view(),
        name="account_email_verification_sent"
    ),
    url(r"^confirm-email/(?P<key>[-:\w]+)/$", sso.user.views.ConfirmEmailView.as_view(), name="account_confirm_email"),
    url(r"^password/set/$", allauth.account.views.password_set, name="account_set_password"),
    url(r"^password/reset/$", sso.user.views.PasswordResetView.as_view(), name="account_reset_password"),
    url(
        r"^password/change/$",
        login_required(sso.user.views.PasswordChangeView.as_view()),
        name="account_change_password"
    ),
    url(r"^password/reset/done/$", allauth.account.views.password_reset_done, name="account_reset_password_done"),
    url(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        sso.user.views.PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key"
    ),
]

oauth2_provider_patterns = [
    url(r'^user-profile/v1/$', sso.oauth2.views_user.UserRetrieveAPIView.as_view(), name='user-profile'),
    url(r'^authorize/$', sso.oauth2.views_user.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', sso.oauth2.views_user.TokenView.as_view(), name="token"),
    url(r'^revoke_token/$', sso.oauth2.views_user.RevokeTokenView.as_view(), name="revoke-token"),
]

api_urlpatterns = [
    url(r'^healthcheck/$', directory_healthcheck.views.HealthcheckView.as_view(), name='healthcheck'),
    url(r'^healthcheck/ping/$', directory_healthcheck.views.PingView.as_view(), name='healthcheck-ping'),
    url(r'^session-user/$', sso.api.views_user.SessionUserAPIView.as_view(), name='session-user'),
    url(r'^last-login/$', sso.api.views_user.LastLoginAPIView.as_view(), name='last-login'),
    url(r'^password-check/$', sso.api.views_user.PasswordCheckAPIView.as_view(), name='password-check'),
    url(
        r'^activity-stream/$',
        sso.api.views_activity_stream.ActivityStreamViewSet.as_view({'get': 'list'}),
        name='activity-stream'
    ),
    url(
        r'^verification-code/regenerate/$',
        sso.verification.views.RegenerateCodeCreateAPIView.as_view(),
        name='verification-code-regenerate'
    ),
    url(
        r'^verification-code/verify/$',
        sso.verification.views.VerifyVerificationCodeAPIView.as_view(),
        name='verification-code-verify'
    ),
    url(r'^user/$', sso.user.views_api.UserCreateAPIView.as_view(), name='user'),
    url(r'^user/profile/$', sso.user.views_api.UserProfileCreateAPIView.as_view(), name='user-create-profile'),
    url(r'^user/profile/update/$', sso.user.views_api.UserProfileUpdateAPIView.as_view(), name='user-update-profile'),
    url(r'^user/page-view/$', sso.user.views_api.UserPageViewAPIView.as_view(), name='user-page-views'),
]

testapi_urls = [
    url(r'^user-by-email/(?P<email>.*)/$', sso.testapi.views.UserByEmailAPIView.as_view(), name='user_by_email'),
    url(r'^test-users/$', sso.testapi.views.TestUsersAPIView.as_view(), name='test_users'),
]

urlpatterns = [
    url(r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    url(r"^robots\.txt$", directory_components.views.RobotsView.as_view(), name='robots'),
    url(r"^$", sso.user.views.SSOLandingPage.as_view(), name="sso_root"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include(allauth_urlpatterns)),
    url(r'^oauth2/', include((oauth2_provider_patterns, 'oauth2_provider'), namespace='oauth2_provider')),
    url(r'^api/v1/', include((api_urlpatterns, 'api'), namespace='api')),
    url(r'^testapi/', include((testapi_urls, 'testapi'), namespace='testapi')),
    url(r'^login-providers/', include(allauth.urls.provider_urlpatterns)),
    url(r'^social/', include(allauth.socialaccount.urls)),

    url(r'^accounts/login/via-linkedin/', sso.user.views.LoginViaLinkedinView.as_view(), name='login-via-linkedin'),
    url(r'^accounts/login/via-google/', sso.user.views.LoginViaGoogleView.as_view(), name='login-via-google'),
]


if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    authbroker_urls = [
        url(r'^admin/login/$', RedirectView.as_view(url=reverse_lazy('authbroker_client:login'), query_string=True)),
        url('^auth/', include('authbroker_client.urls')),
    ]
    urlpatterns = [url('^', include(authbroker_urls))] + urlpatterns
