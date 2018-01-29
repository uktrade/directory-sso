from django.conf.urls import url

from testapi.views import UserByEmailAPIView

urlpatterns = [
    url(
        r'^user-by-email/(?P<email>.*)/$',
        UserByEmailAPIView.as_view(),
        name='user_by_email'
    )
]
