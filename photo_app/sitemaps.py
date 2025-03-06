# photo_app/sitemaps.py
from django.contrib.sitemaps import GenericSitemap
from .models import Photo3, PageContent, Review, InstagramPost

review_info_dict = {
    "queryset": Review.objects.all(),
    "date_field": "review_date",  # Use the appropriate date field
}


pagecontent_info_dict = {
    "queryset": PageContent.objects.all(),
}

sitemaps = {
    "review": GenericSitemap(review_info_dict, priority=0.7),
    "pagecontent": GenericSitemap(pagecontent_info_dict, priority=0.8),
}
