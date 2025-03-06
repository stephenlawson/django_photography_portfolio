from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import (
    Photo3,
    InstagramPost,
    Comment,
    Contact,
    Review,
    PageContent,
    Event,
    AccessRequest,
    Category,
    ClientGallery,
    Photo4,
    ServiceCategory,
    Service,
    AddOn,
    PriceTier,
    EmailCampaign,
    EmailLog,
    Video,
    CherryBlossomSession
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.urls import path
from django.http import HttpResponseRedirect
from django.template import Template, Context
from django.utils import timezone
from django.contrib import messages
import pandas as pd
import smtplib
from django.conf import settings
import io
import os
from urllib.request import urlopen


@admin.register(Photo3)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "image")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "photo", "user", "content")


@admin.register(InstagramPost)
class InstagramPostAdmin(admin.ModelAdmin):
    list_display = ("post_id", "permalink", "media_url", "timestamp")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "service",
        "package",
        "email",
        "phone",
        "date",
        "location",
        "updated",
    )
    list_filter = ("service", "updated", "date")
    search_fields = (
        "first_name",
        "last_name",
        "email",
        "service",
        "package",
        "location",
    )
    readonly_fields = ("updated",)
    date_hierarchy = "date"

    fieldsets = (
        (
            "Personal Information",
            {"fields": (("first_name", "last_name"), ("email", "phone"))},
        ),
        ("Service Details", {"fields": (("service", "package"), "date", "location")}),
        ("Additional Information", {"fields": ("additional_info", "updated")}),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "Name"

    def get_ordering(self, request):
        return ["-updated"]  # Most recent inquiries first


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("author_name", "rating")


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("page_id",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date")
    search_fields = ("name",)
    ordering = ("-date",)


@admin.register(AccessRequest)
class AccessRequestAdmin(ImportExportModelAdmin):
    list_display = ("name", "email", "event", "request_date")
    list_filter = ("event", "request_date")
    search_fields = ("name", "email")
    ordering = ("-request_date",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "intro_text")


@admin.register(ClientGallery)
class ClientGalleryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "date", "gallery_text")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Photo4)
class Photo4Admin(admin.ModelAdmin):
    list_display = ("gallery", "image")


class AddOnInline(admin.TabularInline):
    model = AddOn
    extra = 1


class PriceTierInline(admin.TabularInline):
    model = PriceTier
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "base_price", "duration")
    list_filter = ("category",)
    inlines = [AddOnInline, PriceTierInline]


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'gallery', 'order', 'created_at')
    list_filter = ('gallery', 'created_at')
    search_fields = ('title', 'description', 'gallery__name')
    ordering = ('order', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    change_form_template = 'admin/photo_app/emailcampaign/change_form.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/send/',
                self.admin_site.admin_view(self.send_campaign),
                name='photo_app_emailcampaign_send',
            ),
        ]
        return custom_urls + urls
    
    def send_campaign(self, request, object_id):
        try:
            clean_id = object_id.split('/')[0]
            campaign = EmailCampaign.objects.get(id=clean_id)
            
            # Read CSV file with debug info
            print("\nReading CSV file...")
            csv_file = campaign.contact_list.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_file))
            print(f"CSV Columns: {df.columns.tolist()}")
            print(f"First row sample: {df.iloc[0].to_dict()}")
            
            # Load email template
            template_path = 'admin/photo_app/emailcampaign/email_template.html'
            with open(os.path.join(settings.BASE_DIR, 'photo_app', 'templates', template_path), 'r') as template_file:
                base_template = template_file.read()

            # Get event type display name
            event_type_display = dict(EmailCampaign.EVENT_TYPES).get(campaign.event_type, campaign.event_type)
            
            # Prepare image attachments
            image_dict = {
                'header': ('header.jpg', campaign.header_image.read()),
                'google': ('google.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/google.png').read()),
                'facebook': ('facebook.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/facebook.png').read()),
                'yelp': ('yelp.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/yelp.png').read()),
                'instagram': ('instagram.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/instagram.png').read()),
                'venmo': ('venmo.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/venmo.png').read()),
                'paypal': ('paypal.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/paypal.png').read()),
                'cashapp': ('cashapp.png', urlopen('https://django-portfolio-apps.s3.us-east-1.amazonaws.com/photo_app/icons/cashapp.png').read()),
            }
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                
                for index, row in df.iterrows():
                    try:
                        msg = MIMEMultipart("related")
                        msg["From"] = settings.EMAIL_HOST_USER
                        msg["To"] = row["Email"]
                        msg["Subject"] = f"Your Photos are Ready! - {campaign.name}"
                        
                        # Create the HTML part
                        msg_alternative = MIMEMultipart("alternative")
                        msg.attach(msg_alternative)
                        
                        # Attach images and create image dictionary for template
                        image_cids = {}
                        for img_id, (filename, img_data) in image_dict.items():
                            image = MIMEImage(img_data)
                            image.add_header('Content-ID', f'<{img_id}>')
                            msg.attach(image)
                            image_cids[img_id] = f"cid:{img_id}"
                        
                        try:
                            # Format template with debug info
                            print("Formatting template...")
                            html_content = base_template.format(
                                recipient_name=row["Name"],
                                header_image_url=image_cids['header'],
                                gallery_link=campaign.gallery_link,
                                email_content=campaign.email_content.format(recipient_name=row["Name"]), 
                                event_type=event_type_display.lower(),
                                google_icon=image_cids['google'],
                                facebook_icon=image_cids['facebook'],
                                yelp_icon=image_cids['yelp'],
                                instagram_icon=image_cids['instagram'],
                                venmo_icon=image_cids['venmo'],
                                paypal_icon=image_cids['paypal'],
                                cashapp_icon=image_cids['cashapp']
                            )
                            print("Template formatted successfully")
                        except Exception as format_error:
                            print(f"Error formatting template: {str(format_error)}")
                            raise
                        
                        msg_alternative.attach(MIMEText(html_content, "html"))
                        server.sendmail(settings.EMAIL_HOST_USER, row["Email"], msg.as_string())
                        
                        EmailLog.objects.create(
                            campaign=campaign,
                            recipient_name=row["Name"],
                            recipient_email=row["Email"],
                            status="sent"
                        )
                        
                    except Exception as e:
                        EmailLog.objects.create(
                            campaign=campaign,
                            recipient_name=row["Name"],
                            recipient_email=row["Email"],
                            status="failed",
                            error_message=str(e)
                        )
            
            campaign.sent_at = timezone.now()
            campaign.save()
            
            self.message_user(request, "Email campaign sent successfully!", messages.SUCCESS)
            
        except Exception as e:
            self.message_user(request, f"Error sending campaign: {str(e)}", messages.ERROR)
        
        return HttpResponseRedirect("../../")

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            try:
                campaign = EmailCampaign.objects.get(id=object_id)
                if not campaign.sent_at:
                    extra_context['show_send_button'] = True
            except EmailCampaign.DoesNotExist:
                pass
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    list_display = ('name', 'event_type', 'event_date', 'created_at', 'sent_at')
    list_filter = ('event_type', 'sent_at')
    search_fields = ('recipient_name',)
    readonly_fields = ('created_at', 'sent_at')
    
    fieldsets = (
        ('Campaign Details', {
            'fields': ('name', 'event_type', 'event_date', 'header_image', 'gallery_link')
        }),
        ('Email Content', {
            'fields': ('email_content',)
        }),
        ('Contact List', {
            'fields': ('contact_list',)
        }),
        ('Campaign Status', {
            'fields': ('created_at', 'sent_at')
        })
    )

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'recipient_name', 'recipient_email', 'sent_at', 'status')
    list_filter = ('campaign', 'status', 'sent_at')
    search_fields = ('recipient_name', 'recipient_email')
    readonly_fields = ('campaign', 'recipient_name', 'recipient_email', 'sent_at', 'status', 'error_message')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
@admin.register(CherryBlossomSession)
class CherryBlossomSessionAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'end_time', 'is_booked', 'client_name', 'client_email')
    list_filter = ('date', 'is_booked')
    search_fields = ('client_name', 'client_email')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Session Details', {
            'fields': ('date', 'start_time', 'end_time', 'duration', 'price', 'location')
        }),
        ('Booking Status', {
            'fields': ('is_booked', 'client_name', 'client_email')
        }),
    )
    
    # Add actions for bulk operations
    actions = ['mark_as_booked', 'mark_as_available']
    
    def mark_as_booked(self, request, queryset):
        queryset.update(is_booked=True)
        self.message_user(request, f"{queryset.count()} sessions marked as booked.")
    mark_as_booked.short_description = "Mark selected sessions as booked"
    
    def mark_as_available(self, request, queryset):
        queryset.update(is_booked=False, client_name=None, client_email=None)
        self.message_user(request, f"{queryset.count()} sessions marked as available.")
    mark_as_available.short_description = "Mark selected sessions as available"