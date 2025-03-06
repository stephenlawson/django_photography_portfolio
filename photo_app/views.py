from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
import zipfile
import json
import os
import io
from django.core.files.base import ContentFile
from PIL import Image
from PIL import Image
from urllib.request import urlopen
from django.core.cache import cache
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.contrib import messages
from django.urls import reverse
from .seo_content.loader import SEOLoader
from .forms import ContactForm, GalleryAccessRequestForm
from .models import (
    Photo3,
    Comment,
    InstagramPost,
    Review,
    PageContent,
    AccessRequest,
    Event,
    Category,
    ClientGallery,
    Photo4,
    ServiceCategory,
    Service,
    CherryBlossomSession
)
from photo_blog.models import BlogPost
from django.utils import timezone

def format_phone_number(phone):
    """
    Format phone number as (###) ###-####
    Removes any non-digit characters first
    """
    # Remove any non-digit characters

    phone_str = str(phone)

    if phone_str.startswith("+1"):
        phone_str = phone_str[2:]
    digits = "".join(filter(str.isdigit, phone_str))

    # If we don't have exactly 10 digits, return original
    if len(digits) != 10:
        return phone

    # Format as (###) ###-####
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


def portfolio_view(request):
    seo = SEOLoader()
    cache_key = "portfolio_categories"
    categories = cache.get(cache_key)
    if not categories:
        categories = Category.objects.filter(parent=None).order_by("order", "name")
        cache.set(cache_key, categories, 3600)  # Cache for 1 hour
    insta_posts = InstagramPost.objects.all().order_by("-timestamp")[:12]
    reviews = Review.objects.all().order_by("-review_date")
    photo_blogs = BlogPost.objects.all().order_by('-created_at')[:3]
    total_reviews = reviews.count()
    if total_reviews > 0:
        average_rating = sum(review.rating for review in reviews) / total_reviews
        average_rating = round(average_rating, 1)
    else:
        average_rating = 0
    page_content = PageContent.objects.filter(page_id="index").first()
    for review in reviews:
        review.stars = range(review.rating)
    image_numbers = range(1, 20)

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            field_value = form.cleaned_data["additional_info"]
            if any(
                keyword.lower() in field_value.lower()
                for keyword in settings.BLOCKED_KEYWORDS
            ):
                messages.error(
                    request, "Form submission blocked due to inappropriate content."
                )
                return render(
                    request,
                    "photo_app/index.html",
                    {
                        "form": form,
                        "insta_posts": insta_posts,
                        "image_numbers": image_numbers,
                    },
                )

            form.save()
            # Send email notification
            send_mail(
                subject=f"Contact Form: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']} - {form.cleaned_data['service']}",
                message=f"""Name: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}
                Email: {form.cleaned_data['email']}
                Phone: {format_phone_number(form.cleaned_data['phone'])}
                Service: {form.cleaned_data['service']}
                Date: {form.cleaned_data['date']}
                Location: {form.cleaned_data['location']}
                Additional Info: {form.cleaned_data['additional_info']}""",
                from_email=form.cleaned_data["email"],
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            messages.success(
                request,
                f"Thank you for your inquiry, {form.cleaned_data['first_name']}",
            )
            return redirect("/form-received")
        else:
            messages.warning(request, "Form was not valid.")
    else:
        form = ContactForm(
            show_package=False
        )  # No service or package needed for index page form

    page_seo = seo.get_page_seo("portfolio")
    location = seo.get_location("richmond")
    schema = seo.get_schema("portfolio")
    breadcrumbs = [
        {"name": "Home", "url": reverse("index")},
    ]

    context = {
        "form": form,
        "insta_posts": insta_posts,
        "reviews": reviews,
        "photo_blogs": photo_blogs,
        "image_numbers": image_numbers,
        "page_content": page_content,
        "categories": categories,
        "average_rating": average_rating,  # Add this
        "total_reviews": total_reviews,  # Add this
        "meta": {
            "title": page_seo.get("meta", {}).get("title"),
            "description": page_seo.get("meta", {}).get("description"),
            "canonical_url": request.build_absolute_uri(),
            "og": page_seo.get("og", {}),
            "keywords": page_seo.get("meta", {}).get("keywords"),
        },
        "location": location,
        "schema": schema,
        "seo": page_seo,
    }
    return render(request, "photo_app/index.html", context)


def gallery_list(request, category_slug):
    seo = SEOLoader()
    category = get_object_or_404(Category, name=category_slug)
    subcategories = category.subcategories.all()
    galleries = category.galleries.all().order_by("-date")
    category_seo = seo.get_category_seo(category_slug)

    breadcrumbs = [
        {"name": "Home", "url": reverse("index")},
        {"name": "Portfolio", "url": reverse("portfolio")},
        {"name": category.get_name_display(), "url": None},
    ]

    location = None
    if category.name in [
        "richmond",
        "virginia-beach",
        "norfolk",
    ]:  # Add your location categories
        location = seo.get_location(category.name)

    context = {
        "category": category,
        "subcategories": subcategories,
        "galleries": galleries,
        "breadcrumbs": breadcrumbs,
        "seo": category_seo,
        "location": location,
        "meta": {
            "title": f"{category.get_name_display()} Photography - Stephen Lawson Photography",
            "description": (
                category.intro_text
                if category.intro_text
                else f"View my {category.get_name_display().lower()} photography portfolio"
            ),
            "canonical_url": request.build_absolute_uri(),
        },
    }

    return render(request, "photo_app/gallery_list.html", context)


def photo_gallery(request, gallery_slug):
    """Individual gallery view with SEO"""
    # Get gallery and photos
    gallery = get_object_or_404(ClientGallery, slug=gallery_slug)
    photos = gallery.photos.all()

    # Calculate photo orientation statistics for optimal layout
    portrait_count = photos.filter(orientation="portrait").count()
    landscape_count = photos.filter(orientation="landscape").count()

    # Build breadcrumbs
    breadcrumbs = [
        {"name": "Home", "url": reverse("index")},
        {"name": "Portfolio", "url": reverse("portfolio")},
        {
            "name": gallery.category.get_name_display(),
            "url": reverse("gallery_list", args=[gallery.category.name]),
        },
        {"name": gallery.name, "url": None},
    ]

    # Build schema for the photo gallery
    gallery_schema = {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": gallery.name,
        "description": gallery.gallery_text,
        "about": {"@type": "PhotographyBusiness", "name": "Stephen Lawson Photography"},
        "datePublished": gallery.date.isoformat(),
        "image": [photo.image.url for photo in photos[:5]],  # First 5 photos
    }

    context = {
        "gallery": gallery,
        "photos": photos,
        "breadcrumbs": breadcrumbs,
        "portrait_count": portrait_count,
        "landscape_count": landscape_count,
        "schema": gallery_schema,
        "meta": {
            "title": f"{gallery.name} - Photography Gallery by Stephen Lawson",
            "description": (
                gallery.gallery_text
                if gallery.gallery_text
                else f"View our {gallery.name} photography gallery"
            ),
            "canonical_url": request.build_absolute_uri(),
            "og": {
                "title": gallery.name,
                "description": gallery.gallery_text,
                "image": gallery.cover_photo.url if gallery.cover_photo else None,
                "type": "article",
            },
        },
    }

    return render(request, "photo_app/photo_gallery.html", context)


def thank_you_booking(request):
    return render(request, "photo_app/thank_you_booking.html")


def form_received(request):
    return render(request, "photo_app/form_received.html")


def more_about(request):
    page_content = PageContent.objects.filter(page_id="more-about").first()
    context = {"page_content": page_content}
    return render(request, "photo_app/more_about.html", context)


def portfolio(request):
    # Add logic to fetch galleries and shoots
    return render(request, "photo_app/portfolio.html")


def services(request):
    return render(request, "photo_app/services.html")


def portraits(request):
    return render(request, "photo_app/portraits.html")


def senior(request):
    return render(request, "photo_app/senior.html")


def wedding(request):
    return render(request, "photo_app/wedding.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")  # Redirect to the index page
        else:
            # Invalid credentials, display an error message
            messages.error(request, f"Invalid credentials.")
            return redirect("login")

    return render(request, "photo_app/login.html")


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def user_photo_gallery(request):
    user = request.user
    photos = Photo3.objects.filter(image__contains="_thumb", user=user)
    photos_full = Photo3.objects.filter(image__contains="_full", user=user)
    total_likes = Photo3.objects.filter(is_liked=True).count()
    # Calculate total comments using annotations
    total_comments = photos.annotate(num_comments=Count("comments")).aggregate(
        total_comments=Sum("num_comments")
    )["total_comments"]
    total_comments = total_comments if total_comments else 0
    # Check if total size display is cached
    total_size_display = cache.get("total_size_display")
    if total_size_display is None:
        # Calculate total size if not cached
        total_size_bytes = photos_full.aggregate(total_size=Sum("size_bytes"))[
            "total_size"
        ]
        total_size_display = "0 MB"
        if total_size_bytes is not None:
            total_size_gb = total_size_bytes / (
                1024 * 1024 * 1024
            )  # Convert to GB for readability
            if total_size_gb >= 1:
                total_size_display = (
                    f"{total_size_gb:.2f} GB"  # Display in GB with two decimal places
                )
            else:
                total_size_display = f"{total_size_gb * 1024:.0f} MB"  # Convert to MB and remove decimal places
        # Cache the total size display value
        cache.set("total_size_display", total_size_display)
    context = {
        "user": request.user,
        "photos": photos,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_size_mb": total_size_display,
    }
    return render(request, "photo_app/gallery.html", context)


@login_required
def add_comment(request, photo_id):
    if request.method == "POST":
        photo = get_object_or_404(Photo3, pk=photo_id)
        content = request.POST.get("comment")
        comment = Comment(user=request.user, photo=photo, content=content)
        comment.save()

        data = {
            "success": True,
            "message": "Comment added successfully.",
        }
        return JsonResponse(data)


@csrf_exempt
def toggle_like_status(request, photo_id):
    photo = get_object_or_404(Photo3, id=photo_id)
    photo.is_liked = not photo.is_liked
    photo.save()
    return JsonResponse({"is_liked": photo.is_liked})


def get_like_status(request, photo_id):
    photo = get_object_or_404(Photo3, id=photo_id)
    return JsonResponse({"is_liked": photo.is_liked})


@login_required
def get_comments(request, photo_id):
    if request.method == "GET":
        try:
            photo = Photo3.objects.get(pk=photo_id)
            comments = Comment.objects.filter(photo=photo)
            data = {"comments": []}
            for comment in comments:
                data["comments"].append(
                    {
                        "content": comment.content,
                        "timestamp": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "user": comment.user.username,
                    }
                )
            return JsonResponse(data)
        except Photo3.DoesNotExist:
            return JsonResponse({"error": "Photo not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def download_all_images(request):
    user = request.user
    photos = Photo3.objects.filter(user=user, image__endswith="_full.jpg")
    zip_buffer = io.BytesIO()
    print(photos[0].image.url)
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for photo in photos:
            try:
                image_url = photo.image.url
                image_data = urlopen(image_url).read()
                zip_file.writestr(os.path.basename(image_url), image_data)
            except Exception as e:
                print(f"Error downloading image {photo.id}: {e}")

    # Create a Django response object with the zip file as the content
    response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f"attachment; filename={user.username}_images.zip"
    return response


@login_required
def download_selected_images(request):
    user = request.user
    data = json.loads(request.body)
    selected_photos = data.get("selected_photos", [])
    print(selected_photos)
    photos = Photo3.objects.filter(id__in=selected_photos, user=user)
    print(photos[0].image.url)
    zip_buffer = io.BytesIO()
    # If photos queryset is not empty, proceed to create the zip file
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for photo in photos:
            try:
                image_url = photo.image.url.replace("_thumb", "_full")
                image_data = urlopen(image_url).read()
                zip_file.writestr(os.path.basename(image_url), image_data)
            except Exception as e:
                print(f"Error downloading image {photo.id}: {e}")

    # Create a Django response object with the zip file as the content
    response = HttpResponse(zip_buffer.getvalue(), content_type="application/zip")
    response["Content-Disposition"] = f"attachment; filename={user.username}_images.zip"
    return response


@login_required
def download_single_image(request):
    user = request.user
    image_id = request.GET.get("image_id")
    if image_id is not None:
        try:
            photo = Photo3.objects.get(id=image_id, user=user)
            image_url = photo.image.url.replace("_thumb", "_full")
            image_data = urlopen(image_url).read()
            response = HttpResponse(image_data, content_type="image/jpeg")
            response["Content-Disposition"] = (
                f"attachment; filename={os.path.basename(image_url)}"
            )
            return response
        except Photo3.DoesNotExist:
            return HttpResponse("Image not found.", status=404)
    else:
        return HttpResponse("Image ID parameter is missing.", status=400)


@login_required
def upload_photos(request):
    if request.method == "POST":
        try:
            gallery_id = request.POST.get("gallery")
            if not gallery_id:
                return JsonResponse({"error": "Gallery not selected"}, status=400)

            gallery = get_object_or_404(ClientGallery, id=gallery_id)

            if "images" not in request.FILES:
                return JsonResponse({"error": "No files uploaded"}, status=400)

            files = request.FILES.getlist("images")
            if not files:
                return JsonResponse({"error": "No files in request"}, status=400)

            for image_file in files:
                try:
                    # Create the photo instance with the original image
                    photo = Photo4(gallery=gallery, image=image_file)

                    # Open image and determine orientation before saving
                    img = Image.open(image_file)
                    width, height = img.size
                    aspect_ratio = width / height

                    # Use a threshold to determine orientation
                    # Images very close to square will be treated as portrait
                    photo.orientation = (
                        "landscape" if aspect_ratio > 1.2 else "portrait"
                    )

                    photo.save()

                    # Convert to RGB if necessary (for PNG files)
                    if img.mode != "RGB":
                        img = img.convert("RGB")

                    # Calculate thumbnail size while maintaining aspect ratio
                    orig_width, orig_height = img.size
                    if orig_width > orig_height:
                        new_width = 600
                        new_height = int(600 * (orig_height / orig_width))
                    else:
                        new_height = 600
                        new_width = int(600 * (orig_width / orig_height))

                    # Resize the image
                    img = img.resize(
                        (new_width, new_height), resample=Image.Resampling.LANCZOS
                    )

                    # Save thumbnail
                    thumb_io = io.BytesIO()
                    img.save(thumb_io, "JPEG", quality=85)
                    thumb_io.seek(0)

                    # Generate thumbnail filename
                    original_filename = os.path.splitext(
                        os.path.basename(photo.image.name)
                    )[0]
                    thumbnail_filename = f"{original_filename}_thumb.jpg"

                    # Save thumbnail to model
                    photo.thumbnail.save(
                        thumbnail_filename, ContentFile(thumb_io.getvalue()), save=False
                    )

                    # Update size_bytes field
                    if hasattr(image_file, "size"):
                        photo.size_bytes = image_file.size

                    photo.save()

                except Exception as e:
                    return JsonResponse(
                        {"error": f"Error saving image: {str(e)}"}, status=500
                    )

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)

    try:
        # Get the film category and its subcategories
        film_category = Category.objects.get(name="film")
        film_subcategories = Category.objects.filter(parent=film_category)

        # Get all galleries including those from film subcategories
        galleries = (
            ClientGallery.objects.select_related("category")
            .all()
            .order_by("category__name", "name")
        )

        # Create context for template
        context = {
            "galleries": galleries,
            "film_category": film_category,
            "film_subcategories": film_subcategories,
        }

        return render(request, "photo_app/upload_photos.html", context)

    except Exception as e:
        messages.error(request, f"Error loading galleries: {str(e)}")
        return redirect("index")


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler500(request):
    return render(request, "errors/500.html", status=500)


def handler400(request, exception):
    return render(request, "errors/400.html", status=400)


def handler403(request, exception):
    return render(request, "errors/403.html", status=403)


def handler405(request, exception):
    return render(request, "errors/405.html", status=405)


def handler410(request, exception):
    return render(request, "errors/410.html", status=410)


def privacy_policy(request):
    return render(request, "photo_app/privacy_policy.html")


def terms_of_service(request):
    return render(request, "photo_app/terms_of_service.html")


def accessibility(request):
    return render(request, "photo_app/accessibility.html")


def gallery_access_request(request, event_slug=None):
    if event_slug:
        # Get the event based on the slug
        event = get_object_or_404(Event, slug=event_slug)
        event_provided = True
    else:
        event = None
        event_provided = False

    if request.method == "POST":
        form = GalleryAccessRequestForm(
            request.POST, event_provided=event_provided, event=event
        )
        if form.is_valid():
            # Save the access request to the database

            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            comments = form.cleaned_data["comments"]

            if event_provided:
                selected_event = event
            else:
                selected_event = form.cleaned_data["event"]

            # Save the access request to the database
            AccessRequest.objects.create(
                name=name,
                email=email,
                event=selected_event,
                comments=comments,
            )
            messages.success(request, f"Thank you for your access request!")
            return redirect("/form-received")
        else:
            messages.warning(
                request, f"Your email has already been received. Thank you!"
            )
    else:
        form = GalleryAccessRequestForm(event_provided=event_provided, event=event)

    context = {
        "form": form,
        "event_provided": event_provided,
        "event": event,
    }

    return render(request, "photo_app/gallery_access_request.html", context)


def gallery_access_thank_you(request):
    return render(request, "photo_app/gallery_access_thank_you.html")


def services_view(request):
    seo = SEOLoader()
    categories = ServiceCategory.objects.all()

    seo_data = seo.get_full_seo("page", "services", request)
    print("Services SEO Data:", seo_data)  # Debug print

    context = {"categories": categories, "seo": seo_data}
    return render(request, "photo_app/services.html", context)


def service_packages_view(request, category_name):
    """Individual service category view with package details"""
    seo = SEOLoader()

    category = get_object_or_404(ServiceCategory, name=category_name)
    services = Service.objects.filter(category=category)

    # Handle specialty services under "other" category
    specialty_service = request.GET.get("type")
    if category_name == "other" and specialty_service:
        seo_data = seo.get_full_seo("service", specialty_service, request)
    else:
        seo_data = seo.get_full_seo("service", category_name, request)

    context = {"category": category, "services": services, "seo": seo_data,}
    return render(request, "photo_app/service_packages.html", context)


def contact_view(request, service=None, package=None):
    # Format service name if it exists
    if service:
        service = service.replace("-", " ").replace("_", " ").title()
    if package:
        package = package.replace("-", " ").replace("_", " ").title()

    if service and package:
        # If the service is "Other Services", use package as service
        if service == "Other Services":
            service = package
            package = None

    if request.method == "POST":
        form = ContactForm(request.POST, service=service, package=package)
        if form.is_valid():
            field_value = form.cleaned_data["additional_info"]
            if any(
                keyword.lower() in field_value.lower()
                for keyword in settings.BLOCKED_KEYWORDS
            ):
                messages.error(
                    request, "Form submission blocked due to inappropriate content."
                )
                return render(request, "photo_app/contact.html", {"form": form})

            form.save()
            # Send email notification
            send_mail(
                subject=f"Contact Form: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']} - {form.cleaned_data['service']}",
                message=f"""Name: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}
                Email: {form.cleaned_data['email']}
                Phone: {format_phone_number(form.cleaned_data['phone'])}
                Service: {form.cleaned_data['service']}
                Package: {form.cleaned_data['package'] if form.cleaned_data.get('package') else 'Not specified'}
                Date: {form.cleaned_data['date']}
                Location: {form.cleaned_data['location']}
                Additional Info: {form.cleaned_data['additional_info']}""",
                from_email=form.cleaned_data["email"],
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            messages.success(
                request,
                f"Thank you for your inquiry, {form.cleaned_data['first_name']}",
            )
            return redirect("/form-received")
        else:
            messages.warning(request, "Form was not valid.")
    else:
        # Special handling for "Other Services"
        if service == "Other Services":
            if package in ["Maternity", "Newborn", "Car", "Real Estate"]:
                service = package
                package = None

        form = ContactForm(service=service, package=package)

    context = {"form": form, "selected_service": service, "selected_package": package}
    return render(request, "photo_app/contact.html", context)


def serve_robots_txt(request):
    """Serve robots.txt from photo_app directory"""
    content = """# robots.txt for stephen.photography
User-agent: *
Allow: /

# Sitemap
Sitemap: https://stephen.photography/sitemap.xml

# Common directories in photo_app
Allow: /photo_app/gallery/
Allow: /photo_app/gallery/website_galleries/
Allow: /photo_app/gallery/images/
Allow: /photo_app/img/
Allow: /photo_app/category_images/
Allow: /photo_app/insta_thumbnails/
Allow: /photo_app/review_thumbnails/
Allow: /photo_app/css/
Allow: /photo_app/js/

# Crawl-delay suggestion
Crawl-delay: 1"""
    return HttpResponse(content, content_type="text/plain")


def second_shooter_view(request):
    # Initialize SEO loader
    seo = SEOLoader()
    
    # Get page content using existing fields
    page_content = PageContent.objects.filter(page_id="second-shooter").first()
    
    # Get SEO content from yaml file
    seo_data = seo.get_full_seo('page', 'second-shooter', request)

    # Get page content using existing fields
    page_content = PageContent.objects.filter(page_id="second-shooter").first()

    # Parse equipment JSON from existing fields
    equipment = {
        "cameras": (
            json.loads(page_content.page_content2)
            if page_content and page_content.page_content2
            else {}
        ),
        "lighting": (
            json.loads(page_content.page_content3)
            if page_content and page_content.page_content3
            else []
        ),
        "accessories": (
            json.loads(page_content.page_content4)
            if page_content and page_content.page_content4
            else []
        ),
    }

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            field_value = form.cleaned_data["additional_info"]
            if any(
                keyword.lower() in field_value.lower()
                for keyword in settings.BLOCKED_KEYWORDS
            ):
                messages.error(
                    request, "Form submission blocked due to inappropriate content."
                )
                return render(request, "photo_app/second_shooter.html", {"form": form})

            form.save()

            # Send email notification
            send_mail(
                subject=f"Contact Form: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']} - {form.cleaned_data['service']}",
                message=f"""Name: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}
                Email: {form.cleaned_data['email']}
                Phone: {format_phone_number(form.cleaned_data['phone'])}
                Service: {form.cleaned_data['service']}
                Package: {form.cleaned_data.get('package', 'Not specified')}
                Date: {form.cleaned_data['date']}
                Location: {form.cleaned_data['location']}
                Additional Info: {form.cleaned_data['additional_info']}""",
                from_email=form.cleaned_data["email"],
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            messages.success(
                request,
                f"Thank you for your inquiry, {form.cleaned_data['first_name']}",
            )
            return redirect("/form-received")
        else:
            messages.warning(request, "Form was not valid.")
    else:
        form = ContactForm()

    breadcrumbs = [
        {"name": "Home", "url": reverse("index")},
        {"name": "Second Shooter", "url": None},
    ]

    # Get schema from SEO loader
    schema = seo.get_schema('second-shooter')

    context = {
        'form': form,
        'page_content': page_content,
        'equipment': equipment,
        'breadcrumbs': breadcrumbs,
        'seo': seo_data,
        'schema': schema,
        'meta': {
            'title': seo_data.get('meta', {}).get('title', "Second Shooter - Stephen Lawson Photography"),
            'description': seo_data.get('meta', {}).get('description', ""),
            'keywords': seo_data.get('meta', {}).get('keywords', ""),
            'canonical_url': request.build_absolute_uri(),
            'og': seo_data.get('meta', {}).get('og', {})
        }
    }

    return render(request, "photo_app/second_shooter.html", context)

def cherry_blossom_booking(request):
    """View for the Cherry Blossom mini session booking page"""
    # Get all available sessions
    seo = SEOLoader()
    mini_service_seo = seo.get_service_seo('mini-sessions', 'cherry_blossom_mini')
    
    # Print for debugging
    print(f"Retrieved SEO data for cherry_blossom_mini: {mini_service_seo}")
    try:
        cherry_service = Service.objects.get(name="Cherry Blossom Mini Sessions")
    except Service.DoesNotExist:
        # Fallback to default values if service doesn't exist
        cherry_service = {
            'name': 'Cherry Blossom Mini Sessions',
            'description': "Capture the beautiful cherry blossoms in Richmond, VA during their peak bloom! These mini sessions at Brown's Island are perfect for couples, families, or individuals looking for stunning spring portraits.",
            'base_price': 125.00,
            'duration': '30 minutes'
        }
    
    # Get default location from CherryBlossomSession model
    cherry_session_location = CherryBlossomSession._meta.get_field('location').default
    
    # Get all available sessions
    available_sessions = CherryBlossomSession.objects.filter(
        date__gte=timezone.now().date(),
        is_booked=False
    ).order_by('date', 'start_time')
    
    # Get unique available dates for the calendar
    available_dates = list(available_sessions.values_list('date', flat=True).distinct())
    available_dates = [date.strftime('%Y-%m-%d') for date in available_dates]
    
    context = {
        'cherry_service': cherry_service,
        'cherry_session_location': cherry_session_location,
        'available_dates': json.dumps(available_dates),
        'seo': mini_service_seo, 
        'meta': {
            'title': mini_service_seo.get('meta', {}).get('title', "Cherry Blossom Mini Sessions | Stephen Lawson Photography"),
            'description': mini_service_seo.get('meta', {}).get('description', "Book your cherry blossom mini session in Richmond, VA."),
            'keywords': mini_service_seo.get('meta', {}).get('keywords', "cherry blossom photos richmond, spring mini sessions"),
            'canonical_url': request.build_absolute_uri(),
        }
    }
    
    # Add breadcrumbs
    breadcrumbs = [
        {"name": "Home", "url": reverse("index")},
        {"name": "Services", "url": reverse("services")},
        {"name": "Mini Sessions", "url": reverse("service_packages", args=["mini-sessions"])},
        {"name": cherry_service.name if hasattr(cherry_service, 'name') else cherry_service['name'], "url": None},
    ]
    context['breadcrumbs'] = breadcrumbs
    
    return render(request, 'photo_app/cherry_blossom_booking.html', context)

def get_available_times(request, date):
    """AJAX view to get all time slots for a specific date, including booked ones"""
    try:
        # Convert date string to date object
        selected_date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get ALL sessions for the date, whether booked or not
        all_slots = CherryBlossomSession.objects.filter(
            date=selected_date
        ).order_by('start_time')
        
        slots = [{
            'id': slot.id,
            'time': slot.start_time.strftime('%I:%M %p'),
            'duration': slot.duration,
            'is_booked': slot.is_booked
        } for slot in all_slots]
        
        return JsonResponse({'slots': slots})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def book_session(request):
    """Handle the booking form submission with enhanced email notification"""
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        client_email = request.POST.get('client_email')
        client_phone = request.POST.get('client_phone')
        selected_date = request.POST.get('selected_date')
        selected_time = request.POST.get('selected_time')
        additional_info = request.POST.get('additional_info', '')
        
        # Check for spam/inappropriate content
        if any(keyword.lower() in additional_info.lower() for keyword in settings.BLOCKED_KEYWORDS):
            return JsonResponse({'error': 'Form submission blocked due to inappropriate content.'}, status=400)
        
        try:
            session = CherryBlossomSession.objects.get(id=session_id, is_booked=False)
            session.is_booked = True
            session.client_name = f"{first_name} {last_name}"
            session.client_email = client_email
            session.save()
            
            # Send email notification
            send_mail(
                subject=f"Cherry Blossom Session Booking: {first_name} {last_name}",
                message=f"""
                Name: {first_name} {last_name}
                Email: {client_email}
                Phone: {format_phone_number(client_phone)}
                Date: {selected_date}
                Time: {selected_time}
                Additional Info: {additional_info}
                """,
                from_email=client_email,
                recipient_list=[settings.EMAIL_HOST_USER],
            )
            
            return JsonResponse({'success': True})
        except CherryBlossomSession.DoesNotExist:
            return JsonResponse({'error': 'Session no longer available'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# Add a dedicated thank you page view for cherry blossom bookings
def cherry_blossom_thank_you(request):
    """Thank you page after successful cherry blossom session booking"""
    return render(request, 'photo_app/thank_you_booking.html')