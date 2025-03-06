# code_portfolio/models.py
from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class Skill(models.Model):
    """Model representing a programming skill or technology"""
    CATEGORY_CHOICES = [
        ('LANGUAGE', 'Programming Language'),
        ('FRAMEWORK', 'Framework/Library'),
        ('DATABASE', 'Database'),
        ('TOOL', 'Tool/Practice'),
        ('CONCEPT', 'Concept'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    icon = models.FileField(upload_to='code_portfolio/skills/', blank=True, null=True)
    description = models.TextField(blank=True)
    proficiency = models.IntegerField(default=0, choices=[(i, f"{i*10}%") for i in range(1, 11)])
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['category', 'order', 'name']
    
    def __str__(self):
        return self.name

class Project(models.Model):
    """Model representing a coding project"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    content = RichTextField()
    featured_image = models.ImageField(upload_to='code_portfolio/projects/')
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    skills = models.ManyToManyField(Skill, related_name='projects')
    
    # Gallery for screenshots
    is_featured = models.BooleanField(default=False)
    date_created = models.DateField()
    date_updated = models.DateTimeField(auto_now=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-date_created']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ProjectImage(models.Model):
    """Model for project gallery images"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='code_portfolio/projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image for {self.project.title}"

class WorkExperience(models.Model):
    """Model representing professional experience"""
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = RichTextField()
    skills_used = models.ManyToManyField(Skill, related_name='work_experiences', blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date', 'order']
    
    def __str__(self):
        return f"{self.position} at {self.company}"

class Education(models.Model):
    """Model representing educational background"""
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.degree} in {self.field_of_study} from {self.institution}"

class Certificate(models.Model):
    """Model representing certifications and courses"""
    name = models.CharField(max_length=200)
    issuer = models.CharField(max_length=200)
    date_obtained = models.DateField()
    description = models.TextField(blank=True)
    url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['-date_obtained']
    
    def __str__(self):
        return f"{self.name} from {self.issuer}"

class Contact(models.Model):
    """Model for contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"