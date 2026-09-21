from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, reverse
from catalog.models import App


class AppSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return App.objects.filter(is_gui=True).only("slug")

    def location(self, obj):
        return f"/app/{obj.slug}/"


class StaticSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return ["home", "app-list", "category-list", "windows-list"]

    def location(self, obj):
        return reverse(obj)


sitemaps = {
    "apps": AppSitemap,
    "static": StaticSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

urlpatterns += i18n_patterns(
    path("", include("catalog.urls")),
    prefix_default_language=False,
)
