# tasks.py
from .models import Review, InstagramPost
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from datetime import datetime
from django.conf import settings
import requests
from PIL import Image
import boto3


def update_reviews(api_key, place_id):
    base_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,user_ratings_total,reviews,url",
        "key": api_key,
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "result" in data:
        place_name = data["result"]["name"]
        rating = data["result"].get("rating", "N/A")
        user_ratings_total = data["result"].get("user_ratings_total", "N/A")

        reviews = data["result"].get("reviews", [])

        # Clear existing reviews for the place
        Review.objects.filter(place_name=place_name).delete()

        # Add new reviews to the database
        for review in reviews:
            Review.objects.create(
                place_name=place_name,
                rating=rating,
                user_ratings_total=user_ratings_total,
                author_name=review.get("author_name", "N/A"),
                review_text=review.get("text", "N/A"),
                post_url=review.get("author_url", ""),
                review_date=datetime.fromtimestamp(review.get("time", None)),
            )


def fetch_and_save_instagram_posts(access_token):
    api_url = f"https://graph.instagram.com/me/media?fields=id,permalink,media_url,timestamp,thumbnail_url,media_type&access_token={access_token}"

    # Fetch Instagram posts
    response = requests.get(api_url)
    data = response.json()

    if not data.get("data"):
        print("no data")
        return  # No posts found

    posts_data = data["data"][:12]  # Get the latest 10 posts

    # Save Instagram posts to the database
    for post_data in posts_data:
        post_id = post_data.get("id")
        if not InstagramPost.objects.filter(post_id=post_id).exists():
            permalink = post_data.get("permalink")
            media_url = post_data.get("media_url")
            timestamp_string = post_data.get("timestamp", "")
            timestamp = (
                timezone.datetime.strptime(timestamp_string, "%Y-%m-%dT%H:%M:%S%z")
                if timestamp_string
                else None
            )
            thumbnail_url = post_data.get("thumbnail_url")
            media_type = post_data.get("media_type")

            # Determine the URL to use for the thumbnail based on media_type
            thumbnail_source_url = thumbnail_url if media_type == "VIDEO" else media_url

            # Download and save thumbnail to S3
            thumbnail_content = requests.get(thumbnail_source_url).content
            thumbnail_filename = f"photo_app/insta_thumbnails/{post_id}_thumbnail.jpg"
            thumbnail_path = default_storage.save(
                thumbnail_filename, ContentFile(thumbnail_content)
            )

            # Resize the thumbnail image (optional)
            thumbnail = Image.open(default_storage.open(thumbnail_path))
            thumbnail.thumbnail((100, 100))  # Adjust the size as needed
            thumbnail.save(default_storage.open(thumbnail_path), "JPEG")

            # Create InstagramPost object and save to the database
            InstagramPost.objects.create(
                post_id=post_id,
                permalink=permalink,
                media_url=media_url,
                timestamp=timestamp,
                thumbnail_url=thumbnail_url,
                media_type=media_type,
                thumbnail=thumbnail_path,  # Save the relative path
            )
