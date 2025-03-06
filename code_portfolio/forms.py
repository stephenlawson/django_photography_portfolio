# code_portfolio/forms.py
from django import forms
from django.conf import settings
from django_recaptcha.fields import ReCaptchaField
from .models import Contact

class ContactForm(forms.ModelForm):
    """Form for the contact page"""
    recaptcha = ReCaptchaField()
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message', 'rows': 5}),
        }