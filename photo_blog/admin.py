from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
