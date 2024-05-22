import allauth.account.views
import allauth.socialaccount
import allauth.urls
import directory_components.views
import directory_healthcheck.views
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import RedirectView

import conf.sitemaps
import sso.api.views_activity_stream
import sso.api.views_user
import sso.oauth2.views_user
import sso.testapi.views
import sso.user.views
import sso.user.views_api
import sso.verification.views
from core.views import PingDomView

sitemaps = {
    'static': conf.sitemaps.StaticViewSitemap,
}


admin.autodiscover()


allauth_urlpatterns = [
    re_path(r"^signup/$", sso.user.views.RedirectToProfileSignUp.as_view(), name="account_signup"),
    re_path(r"^login/$", sso.user.views.LoginView.as_view(), name="account_login"),
    re_path(r"^logout/$", sso.user.views.LogoutView.as_view(), name="account_logout"),
    re_path(r"^inactive/$", allauth.account.views.account_inactive, name="account_inactive"),
    re_path(
        r"^confirm-email/$",
        allauth.account.views.EmailVerificationSentView.as_view(),
        name="account_email_verification_sent",
    ),
    re_path(
        r"^confirm-email/(?P<key>[-:\w]+)/$", sso.user.views.ConfirmEmailView.as_view(), name="account_confirm_email"
    ),
    re_path(r"^password/set/$", allauth.account.views.password_set, name="account_set_password"),
    re_path(r"^password/reset/$", sso.user.views.PasswordResetView.as_view(), name="account_reset_password"),
    re_path(
        r"^password/change/$",
        login_required(sso.user.views.PasswordChangeView.as_view()),
        name="account_change_password",
    ),
    re_path(r"^password/reset/done/$", allauth.account.views.password_reset_done, name="account_reset_password_done"),
    re_path(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        sso.user.views.PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
]

oauth2_provider_patterns = [
    re_path(r'^user-profile/v1/$', sso.oauth2.views_user.UserRetrieveAPIView.as_view(), name='user-profile'),
    re_path(r'^authorize/$', sso.oauth2.views_user.AuthorizationView.as_view(), name="authorize"),
    re_path(r'^token/$', sso.oauth2.views_user.TokenView.as_view(), name="token"),
    re_path(r'^revoke_token/$', sso.oauth2.views_user.RevokeTokenView.as_view(), name="revoke-token"),
]

api_urlpatterns = [
    re_path(r'^healthcheck/$', directory_healthcheck.views.HealthcheckView.as_view(), name='healthcheck'),
    re_path(r'^healthcheck/ping/$', directory_healthcheck.views.PingView.as_view(), name='healthcheck-ping'),
    re_path(r'^session-user/$', sso.api.views_user.SessionUserAPIView.as_view(), name='session-user'),
    re_path(r'^last-login/$', sso.api.views_user.LastLoginAPIView.as_view(), name='last-login'),
    re_path(r'^password-check/$', sso.api.views_user.PasswordCheckAPIView.as_view(), name='password-check'),
    re_path(
        r'^activity-stream/$',
        sso.api.views_activity_stream.ActivityStreamViewSet.as_view({'get': 'list'}),
        name='activity-stream',
    ),
    re_path(
        r'^activity-stream/users/$',
        sso.api.views_activity_stream.ActivityStreamDirectorySSOUsers.as_view(),
        name='activity-stream-users',
    ),
    re_path(
        r'^activity-stream/user-answers-vfm/$',
        sso.api.views_activity_stream.ActivityStreamDirectorySSOUserAnswersVFM.as_view(),
        name='activity-stream-user-answers-vfm',
    ),
    re_path(
        r'^verification-code/regenerate/$',
        sso.verification.views.RegenerateCodeCreateAPIView.as_view(),
        name='verification-code-regenerate',
    ),
    re_path(
        r'^verification-code/verify/$',
        sso.verification.views.VerifyVerificationCodeAPIView.as_view(),
        name='verification-code-verify',
    ),
    re_path(r'^user/$', sso.user.views_api.UserCreateAPIView.as_view(), name='user'),
    re_path(r'^user/profile/$', sso.user.views_api.UserProfileCreateAPIView.as_view(), name='user-create-profile'),
    re_path(
        r'^user/profile/update/$', sso.user.views_api.UserProfileUpdateAPIView.as_view(), name='user-update-profile'
    ),
    re_path(r'^user/page-view/$', sso.user.views_api.UserPageViewAPIView.as_view(), name='user-page-views'),
    re_path(
        r'^user/lesson-completed/$', sso.user.views_api.LessonCompletedAPIView.as_view(), name='user-lesson-completed'
    ),
    re_path(r'^user/questionnaire/$', sso.user.views_api.UserQuestionnaireView.as_view(), name='user-questionnaire'),
    re_path(r'^user/data/$', sso.user.views_api.UserDataView.as_view(), name='user-data'),
]

testapi_urls = [
    re_path(r'^user-by-email/(?P<email>.*)/$', sso.testapi.views.UserByEmailAPIView.as_view(), name='user_by_email'),
    re_path(r'^test-users/$', sso.testapi.views.TestUsersAPIView.as_view(), name='test_users'),
]

urlpatterns = [
    re_path(r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    re_path(r"^robots\.txt$", directory_components.views.RobotsView.as_view(), name='robots'),
    re_path(r"^$", sso.user.views.SSOLandingPage.as_view(), name="sso_root"),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^accounts/', include(allauth_urlpatterns)),
    re_path(r'^oauth2/', include((oauth2_provider_patterns, 'oauth2_provider'), namespace='oauth2_provider')),
    re_path(r'^api/v1/', include((api_urlpatterns, 'api'), namespace='api')),
    re_path(r'^testapi/', include((testapi_urls, 'testapi'), namespace='testapi')),
    re_path(r'^login-providers/', include(allauth.urls.provider_urlpatterns)),
    re_path(r'^social/', include(allauth.socialaccount.urls)),
    re_path(r'^accounts/login/via-linkedin/', sso.user.views.LoginViaLinkedinView.as_view(), name='login-via-linkedin'),
    re_path(r'^accounts/login/via-google/', sso.user.views.LoginViaGoogleView.as_view(), name='login-via-google'),
    path('pingdom/ping.xml', PingDomView.as_view(), name='pingdom'),
]


if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    authbroker_urls = [
        re_path(
            r'^admin/login/$', RedirectView.as_view(url=reverse_lazy('authbroker_client:login'), query_string=True)
        ),
        re_path('^auth/', include('authbroker_client.urls')),
    ]
    urlpatterns = [re_path('^', include(authbroker_urls))] + urlpatterns
