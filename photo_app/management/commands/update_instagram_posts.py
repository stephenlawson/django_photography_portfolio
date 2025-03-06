# yourapp/management/commands/update_instagram_posts.py
from django.core.management.base import BaseCommand
from photo_app.tasks import fetch_and_save_instagram_posts
from django.conf import settings


class Command(BaseCommand):
    help = "Fetch and save Instagram posts and upload thumbnails to S3"

    def handle(self, *args, **options):
        fetch_and_save_instagram_posts(access_token=settings.INSTA_ACCESS_TOKEN)
        self.stdout.write(
            self.style.SUCCESS("Instagram posts and thumbnails updated successfully.")
        )
