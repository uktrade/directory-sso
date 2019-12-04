from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return [
            'account_signup',
            'account_login',
            'account_reset_password',
        ]

    def location(self, item):
        return reverse(item)
