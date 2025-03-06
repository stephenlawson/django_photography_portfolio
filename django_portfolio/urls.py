from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control
from photo_app.sitemap import (
    StaticViewSitemap,
    GallerySitemap,
    CategorySitemap,
    ServiceSitemap,
    BlogSitemap,
    MiniSessionSitemap,
)
from django.views.generic import TemplateView


sitemaps = {
    "static": StaticViewSitemap,
    "galleries": GallerySitemap,
    "categories": CategorySitemap,
    "services": ServiceSitemap,
    "blogs": BlogSitemap,
    'mini_sessions': MiniSessionSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("photo_app.urls")),
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path("photo_blog/", include("photo_blog.urls", namespace="photo_blog")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("code/", include("code_portfolio.urls", namespace="code_portfolio")),
]

handler404 = "photo_app.views.handler404"
handler500 = "photo_app.views.handler500"
handler400 = "photo_app.views.handler400"
handler403 = "photo_app.views.handler403"
handler405 = "photo_app.views.handler405"
handler410 = "photo_app.views.handler410"
