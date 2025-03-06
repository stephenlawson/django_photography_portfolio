# code_portfolio/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Skill,
    Project,
    ProjectImage,
    WorkExperience,
    Education,
    Certificate,
    Contact
)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No Image"

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_created', 'is_featured', 'order', 'preview_image')
    list_filter = ('is_featured', 'skills')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('skills',)
    inlines = [ProjectImageInline]
    
    def preview_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="100" />', obj.featured_image.url)
        return "No Image"

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency', 'order')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(WorkExperience)
class WorkExperienceAdmin(admin.ModelAdmin):
    list_display = ('position', 'company', 'location', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('position', 'company', 'description')
    filter_horizontal = ('skills_used',)

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'field_of_study', 'institution', 'start_date', 'end_date')
    search_fields = ('degree', 'institution', 'field_of_study')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'date_obtained')
    search_fields = ('name', 'issuer')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'date_sent', 'is_read')
    list_filter = ('is_read', 'date_sent')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'date_sent')
    
    def has_add_permission(self, request):
        return False