from django.urls import path
from . import views


app_name = "photo_blog"

urlpatterns = [
    path("", views.blog_post_list, name="photo_blogs"),
    path("<slug:slug>/", views.blog_post_detail, name="photo_blog"),
]
