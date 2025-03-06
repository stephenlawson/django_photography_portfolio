from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User
from django.urls import reverse
from urllib.parse import urlparse
from django.core.files.storage import default_storage
from django.utils.text import slugify
from PIL import Image
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import FileExtensionValidator


class PageContent(models.Model):
    page_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, unique=True, null=True, blank=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(max_length=200, null=True, blank=True)
    page_content = models.TextField(null=True, blank=True)
    page_content2 = models.TextField(null=True, blank=True)
    page_content3 = models.TextField(null=True, blank=True)
    page_content4 = models.TextField(null=True, blank=True)
    page_content5 = models.TextField(null=True, blank=True)
    page_content6 = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Contact(models.Model):
    SERVICE_CHOICES = [
        ("Portrait/Headshot", "Portrait/Headshot"),
        (
            "Studio Portrait/Headshot",
            "Studio Portrait/Headshot",
        ),  # This should match with URL
        ("Wedding", "Wedding"),
        ("Event", "Event"),
        ("Family", "Family"),
        ("Graduation", "Graduation"),
        ("Engagement", "Engagement"),
        ("Couples", "Couples"),
        ("Corporate", "Corporate"),
        ("Second Shooter", "Second Shooter"),
        ("Wedding Videography", "Wedding Videography"),
        ("Event Videography", "Event Videography"),
        ("Other Services", "Other Services"),
    ]
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=200, null=True)
    phone = PhoneNumberField(region="US")
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, null=True)
    package = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True)
    location = models.CharField(max_length=200, null=True)
    additional_info = models.TextField(null=True)
    updated = models.DateField(auto_now_add=True)

    class Meta:
        app_label = "photo_app"

    def __str__(self):
        package_info = f" - {self.package}" if self.package else ""
        return f"{self.first_name} {self.last_name} - {self.service}{package_info}"


class InstagramPost(models.Model):
    post_id = models.CharField(max_length=255)
    permalink = models.TextField()
    media_url = models.TextField()
    timestamp = models.DateTimeField()
    thumbnail_url = models.TextField(null=True)
    media_type = models.CharField(max_length=255)
    thumbnail = models.ImageField(
        upload_to="photo_app/insta_thumbnails"
    )  # Store the relative path in S3

    def __str__(self):
        return f"InstagramPost {self.post_id}"


class Review(models.Model):
    place_name = models.CharField(max_length=255)
    rating = models.IntegerField()
    user_ratings_total = models.IntegerField()
    author_name = models.CharField(max_length=255)
    review_text = models.TextField()
    thumbnail = models.ImageField(
        upload_to="photo_app/review_thumbnails",
        default="photo_app/review_thumbnails/default_thumbnail.jpg",
    )
    post_url = models.URLField(blank=True, null=True)
    review_date = models.DateTimeField(
        blank=True,
        null=True,
    )

    def get_absolute_url(self):
        # Define the URL pattern name for the detail view of your review
        return reverse("photo_app:review_detail", args=[str(self.pk)])

    def __str__(self):
        return f"Review by {self.author_name} on {self.place_name}"


class Photo3(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="photo_app/gallery/images")
    is_liked = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name="liked_photos", blank=True)
    comments = models.ManyToManyField(User, through="Comment")
    size_bytes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Photo {self.id} - User: {self.user.username}"

    def is_liked_by_user(self, user):
        return self.likes.filter(id=user.id).exists()


class Comment(models.Model):
    photo = models.ForeignKey(
        Photo3, on_delete=models.CASCADE, related_name="photo_comments"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.photo}"


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class AccessRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    comments = models.TextField(blank=True)
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access Request from {self.name} for {self.event.name}"

    class Meta:
        unique_together = ("email", "event")


class Category(models.Model):
    CATEGORY_CHOICES = [
        ("graduation", "Graduation"),
        ("portrait", "Portraits"),
        ("engagement", "Engagement"),
        ("wedding", "Wedding"),
        ("family", "Family"),
        ("event", "Event"),
        ("couple", "Couples"),
        ("film", "Film"),
        ("medium_format", "Medium Format"),
        ("35mm", "35mm"),
    ]
    name = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    intro_text = models.TextField(
        null=True, blank=True, help_text="Intro text for the category."
    )
    category_image = models.ImageField(
        upload_to="photo_app/category_images",
        null=True,
        blank=True,
        help_text="Cover image for this category",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )
    order = models.IntegerField(
        default=0,
        help_text="Order in which the category should appear (lower numbers appear first)",
    )

    class Meta:
        ordering = ["order", "name"]  # Default ordering by order field, then name
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.get_name_display()


class ClientGallery(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="galleries"
    )
    name = models.CharField(max_length=200)
    date = models.DateField()
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    cover_photo = models.ImageField(
        upload_to="photo_app/gallery/website_galleries", null=True, blank=True
    )
    gallery_text = models.TextField(
        null=True, blank=True, help_text="Summary for the gallery."
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category})"


class Photo4(models.Model):
    gallery = models.ForeignKey(
        ClientGallery, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="photo_app/gallery/website_galleries")
    thumbnail = models.ImageField(
        upload_to="photo_app/gallery/website_galleries/thumbnails",
        null=True,
        blank=True,
    )
    size_bytes = models.PositiveIntegerField(null=True, blank=True)
    orientation = models.CharField(
        max_length=10,
        choices=[("portrait", "Portrait"), ("landscape", "Landscape")],
        default="landscape",
    )
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Photo {self.image} - Gallery {self.gallery}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=100)
    intro_text = models.TextField(blank=True)
    base_price = models.CharField(
        max_length=100
    )  # Using CharField to allow "From X" format
    duration = models.CharField(max_length=50)
    order = models.IntegerField(default=0)
    cover_image = models.ImageField(
        upload_to="services/categories",
        null=True,
        blank=True,
        help_text="Cover image for the service category",
    )

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.display_name


class Service(models.Model):
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="services"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    extended_description = models.TextField(
        null=True,
        blank=True,
    )
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    price_varies = models.BooleanField(default=False)
    price_display = models.CharField(
        max_length=100, blank=True
    )  # For "From $X" or "Price varies"
    duration = models.CharField(max_length=50)
    header_image = models.ImageField(upload_to="service_headers", blank=True)
    order = models.IntegerField(default=0)
    package_image = models.ImageField(
        upload_to="services/packages",
        null=True,
        blank=True,
        help_text="Image representing this package",
    )

    class Meta:
        ordering = ["category__order", "order"]

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class AddOn(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="addons"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(
        max_length=50, blank=True
    )  # e.g., "per hour", "per location"
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.name} - {self.name}"


class PriceTier(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="price_tiers"
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    condition = models.CharField(
        max_length=200, blank=True
    )  # e.g., "Less than 1000 sq ft"
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.service.name} - {self.name}"

class EmailCampaign(models.Model):
    EVENT_TYPES = [
        ('wedding', 'Wedding'),
        ('elopement', 'Elopement'),
        ('portrait', 'Portrait Session'),
        ('event', 'Event'),
        ('family', 'Family Session'),
        ('graduation', 'Graduation'),
        ('engagement', 'Engagement Session'),
        ('corporate', 'Corporate Event'),
        ('other', 'Other')
    ]
    
    name = models.CharField(max_length=200, help_text="Campaign name for internal reference")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_date = models.DateField(help_text="Date of the event")
    header_image = models.ImageField(
        upload_to='photo_app/gallery/images/',
        help_text="Header image for the email"
    )
    gallery_link = models.URLField(help_text="Link to the photo gallery")
    contact_list = models.FileField(
        upload_to='email_campaigns/contacts/',
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        help_text="CSV file with columns: Name, Email"
    )
    email_content = RichTextUploadingField(
        help_text="Main content of the email. Use {name} to personalize the greeting."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.event_date}"
    
    def get_header_image_url(self):
        if self.header_image:
            return self.header_image.url
        return ''
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Email Campaign'
        verbose_name_plural = 'Email Campaigns'

class EmailLog(models.Model):
    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='logs')
    recipient_name = models.CharField(max_length=200)
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    error_message = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.campaign.name} - {self.recipient_email}"
    
    class Meta:
        ordering = ['-sent_at']

class Video(models.Model):
    gallery = models.ForeignKey(
        ClientGallery, 
        on_delete=models.CASCADE, 
        related_name="videos",
        null=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_file = models.FileField(
        upload_to='photo_app/video/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])]
    )
    thumbnail = models.ImageField(
        upload_to='photo_app/video_thumbnails/', 
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(
        default=0,
        help_text="Order in which the video appears (lower numbers appear first)"
    )

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

    def __str__(self):
        return f"{self.title} - {self.gallery.name}"
    

class CherryBlossomSession(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    location = models.CharField(max_length=200, default="Brown's Island, Richmond, Virginia")
    duration = models.IntegerField(default=30)  # in minutes
    price = models.DecimalField(max_digits=6, decimal_places=2, default=175.00)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    client_email = models.EmailField(blank=True, null=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        
    def __str__(self):
        return f"Cherry Blossom Session - {self.date} at {self.start_time}"