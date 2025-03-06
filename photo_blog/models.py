from django.db import models
from django.urls import reverse
from ckeditor.fields import (
    RichTextField,
)  # Install CKEditor: pip install django-ckeditor
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
from django.contrib.auth.models import User


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    sub_title = models.CharField(max_length=200, null=True, blank=True)
    slug = AutoSlugField(unique=True, populate_from="title")
    content = RichTextUploadingField()

    # SEO Fields
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional custom meta title. If not provided, the post title will be used.",
    )
    meta_description = models.CharField(
        max_length=160,  # Standard SEO meta description length
        blank=True,
        help_text="Brief description for search engines. Keep under 160 characters for best results.",
    )
    meta_keywords = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated keywords for search engines.",
    )

    image = models.ImageField(
        upload_to="photo_app/img/media/",
        null=True,
        blank=True,
        default="photo_app/img/insta-post-4.jpg",
    )
    thumbnail = models.ImageField(
        upload_to="photo_app/img/media/thumbnails/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    profile_photo = models.ImageField(
        upload_to="user_profile_photos/",
        null=True,
        blank=True,
        default="photo_app/img/profile-photo.jpg",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def admin_display(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')} - {self.slug}"

    def get_absolute_url(self):
        return reverse("blog:post_detail", args=[str(self.slug)])

    def get_meta_title(self):
        """Returns meta title with fallback to regular title"""
        if self.meta_title:
            return self.meta_title
        return f"{self.title} | Stephen Lawson Photography Blog"

    def get_meta_description(self):
        """Returns meta description with fallback to subtitle"""
        if self.meta_description:
            return self.meta_description
        return (
            self.sub_title
            if self.sub_title
            else f"Read about {self.title} on the Stephen Lawson Photography blog."
        )
