from django import forms
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from multiupload.fields import MultiImageField
from .models import Contact, AccessRequest, Event
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox


class ContactForm(ModelForm):
    SERVICE_CHOICES = [
        ("Portrait/Headshot", "Portrait/Headshot"),
        (
            "Studio Portrait/Headshot",
            "Studio Portrait/Headshot",
        ),  # This should match with URL
        ("Wedding", "Wedding"),
        ("Wedding_Videography", "Wedding_Videography"),
        ("Event_Videography","Event_Videography"),
        ("Event", "Event"),
        ("Family", "Family"),
        ("Graduation", "Graduation"),
        ("Engagement", "Engagement"),
        ("Couples", "Couples"),
        ("Corporate", "Corporate"),
        ("Wedding Videography", "Wedding Videography"), 
        ("Event Videography", "Event Videography"),
        ("Other Services", "Other Services"),
    ]

    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "John"}),
        required=True,
        label="First Name (required)",
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Doe"}),
        required=True,
        label="Last Name (required)",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "john.doe@email.com"}
        ),
        required=True,
        label="Email (required)",
    )
    phone = PhoneNumberField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "1234567890"}
        ),
        required=False,
        region="US",
    )
    service = forms.ChoiceField(
        choices=SERVICE_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        label="Service (required)",
    )
    package = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "readonly": "readonly",
                "style": "background-color: #f8f9fa;",
            }
        ),
        required=False,
        label="Package",
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        label="Date (required)",
        required=True,
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Specific scenic area, indoor, outdoor, etc.",
            }
        ),
        label="Location (required)",
        required=True,
    )
    additional_info = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "placeholder": "Please provide more details here.",
            }
        ),
        label="Additional Info (required)",
        required=True,
    )

    if settings.TESTING:
        captcha = forms.BooleanField(required=False)
    else:
        captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    def __init__(self, *args, show_package=True, **kwargs):
        service = kwargs.pop("service", None)
        package = kwargs.pop("package", None)
        super().__init__(*args, **kwargs)

        if not show_package:
            del self.fields["package"]

        if service:
            # Convert service to match the choice format (e.g., 'wedding' to 'Wedding')
            service_title = service.replace("-", " ").title()

            service_mapping = {
                "Studio": "Studio Portrait/Headshot",
                "Portrait": "Portrait/Headshot",
                "Other": "Other Services",
                # Add other mappings if needed
            }
            # Find matching service from SERVICE_CHOICES
            matching_service = service_mapping.get(service_title) or next(
                (
                    choice[0]
                    for choice in self.SERVICE_CHOICES
                    if choice[0].lower() == service_title.lower()
                ),
                service_title,
            )

            # Set initial value and make field readonly
            self.fields["service"].initial = matching_service
            self.fields["service"].widget = forms.TextInput(
                attrs={
                    "class": "form-control",
                    "readonly": "readonly",
                    "style": "background-color: #f8f9fa;",
                }
            )
            self.fields["service"].label = "Service (pre-selected)"

        if package:
            self.fields["package"].initial = package.replace("-", " ").title()
            self.fields["package"].label = "Package (pre-selected)"  # Add label

    class Meta:
        model = Contact
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "service",
            "package",
            "date",
            "location",
            "additional_info",
            "captcha",
        ]


class GalleryAccessRequestForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "John Doe"}
        ),
        required=True,
        label="First Name (required)",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "john.doe@email.com"}
        ),
        required=True,
        label="Email (required)",
    )
    comments = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Additional Comments"}
        ),
        label="Additional Comments",
        required=False,
    )
    if settings.TESTING:
        captcha = forms.BooleanField(required=False)
    else:
        captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    def __init__(self, *args, **kwargs):
        # Extract 'event_provided' and 'event' from kwargs
        self.event_provided = kwargs.pop("event_provided", False)
        self.event = kwargs.pop("event", None)
        super().__init__(*args, **kwargs)
        if not self.event_provided:
            # Include the event field only if no event is provided in the URL
            self.fields["event"] = forms.ModelChoiceField(
                queryset=Event.objects.all().order_by("-date"),
                widget=forms.Select(
                    attrs={"class": "form-control", "placeholder": "Select an event"}
                ),
                label="Event (required)",
                required=True,
                empty_label="Select an event",
            )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        # Normalize email to lowercase to handle case sensitivity
        if email:
            email = email.lower()
            cleaned_data["email"] = email  # Update cleaned_data with normalized email
        name = cleaned_data.get("name")
        comments = cleaned_data.get("comments")

        if self.event_provided:
            selected_event = self.event
        else:
            selected_event = cleaned_data.get("event")

        if email and selected_event:
            if AccessRequest.objects.filter(email=email, event=selected_event).exists():
                raise forms.ValidationError(
                    "You have already submitted a request for this event."
                )

        return cleaned_data
