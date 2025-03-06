# management/commands/update_reviews.py
from django.core.management.base import BaseCommand
from photo_app.tasks import update_reviews
import os
import json
from django.conf import settings


class Command(BaseCommand):
    help = "Update reviews from Google Places API"

    def handle(self, *args, **options):
        # Call the Celery task to update reviews
        update_reviews(
            api_key=settings.GOOGLE_API_KEY, place_id=settings.GOOGLE_PLACE_ID
        )
        self.stdout.write(self.style.SUCCESS("Reviews updated successfully."))
