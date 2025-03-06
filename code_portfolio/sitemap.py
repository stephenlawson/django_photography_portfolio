# code_portfolio/sitemap.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Project

class CodeStaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["code_portfolio:home", "code_portfolio:about", "code_portfolio:skills", "code_portfolio:project_list", "code_portfolio:contact"]

    def location(self, item):
        return reverse(item)

class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.date_updated

    def location(self, obj):
        return reverse("code_portfolio:project_detail", args=[obj.slug])