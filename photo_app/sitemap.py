# photo_app/sitemap.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import ClientGallery, Category, Service, ServiceCategory
from photo_blog.models import BlogPost


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(active=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return f"/photo_blog/{obj.slug}/"


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "daily"

    def items(self):
        return ["index", "services", "contact", "more_about"]

    def location(self, item):
        return reverse(item)


class GallerySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ClientGallery.objects.all()

    def location(self, obj):
        return f"/gallery/{obj.slug}/"


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return f"/category/{obj.name}/"


class ServiceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return ServiceCategory.objects.all()

    def location(self, obj):
        return f"/services/{obj.name}/"

class MiniSessionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        # Return list of specific mini session URLs
        return ["cherry_blossom_booking"]

    def location(self, item):
        # Map the item name to the correct URL
        return reverse(item)