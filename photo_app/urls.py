from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.sitemaps.views import sitemap
from .sitemap import (
    StaticViewSitemap,
    GallerySitemap,
    CategorySitemap,
    ServiceSitemap,
    BlogSitemap,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.portfolio_view, name="index"),
    path("more-about/", views.more_about, name="more_about"),
    path("portfolio/", views.portfolio, name="portfolio"),
    path("category/<slug:category_slug>/", views.gallery_list, name="gallery_list"),
    path("gallery/<slug:gallery_slug>/", views.photo_gallery, name="photo_gallery"),
    path("user-gallery/", views.user_photo_gallery, name="user_photo_gallery"),
    path("download_all_images/", views.download_all_images, name="download_all_images"),
    path(
        "download_selected_images/",
        views.download_selected_images,
        name="download_selected_images",
    ),
    path(
        "download_single_image/",
        views.download_single_image,
        name="download_single_image",
    ),
    path(
        "toggle_like_status/<int:photo_id>/",
        views.toggle_like_status,
        name="toggle_like_status",
    ),
    path(
        "get_like_status/<int:photo_id>/", views.get_like_status, name="get_like_status"
    ),
    path("add_comment/<int:photo_id>/", views.add_comment, name="add_comment"),
    path("get_comments/<int:photo_id>/", views.get_comments, name="get_comments"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("upload-photos/", views.upload_photos, name="upload_photos"),
    path("thank-you-for-booking/", views.thank_you_booking, name="thank_you_booking"),
    path("form-received/", views.form_received, name="form_received"),
    path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path("accessibility-statement/", views.accessibility, name="accessibility"),
    path(
        "gallery-access/", views.gallery_access_request, name="gallery_access_request"
    ),
    path(
        "gallery-access/<slug:event_slug>/",
        views.gallery_access_request,
        name="gallery_access_request_event",
    ),
    path("services/", views.services_view, name="services"),
    path(
        "services/<str:category_name>/",
        views.service_packages_view,
        name="service_packages",
    ),
    path("contact/", views.contact_view, name="contact"),
    path("contact/<str:service>/", views.contact_view, name="contact_with_service"),
    path(
        "contact/<str:service>/<str:package>/",
        views.contact_view,
        name="contact_with_package",
    ),
    path("robots.txt", views.serve_robots_txt, name="robots_txt"),
    path("second-shooter/", views.second_shooter_view, name="second_shooter"),
    path('cherry-blossoms-mini/', views.cherry_blossom_booking, name='cherry_blossom_booking'),
    path('cherry-blossoms-mini/times/<str:date>/', views.get_available_times, name='get_available_times'),
    path('cherry-blossoms-mini/book/', views.book_session, name='book_session'),
    path('cherry-blossoms-mini/thank-you/', views.cherry_blossom_thank_you, name='cherry_blossom_thank_you'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
