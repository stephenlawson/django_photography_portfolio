# code_portfolio/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib import messages
from django.db.models import Count
from .models import Project, Skill, WorkExperience, Education, Certificate
from .forms import ContactForm

class HomeView(TemplateView):
    template_name = 'code_portfolio/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get featured projects
        context['featured_projects'] = Project.objects.filter(is_featured=True)[:3]
        # Get skills by category
        context['skills'] = {category[0]: Skill.objects.filter(category=category[0]) 
                            for category in Skill.CATEGORY_CHOICES}
        # Get recent work experience
        context['recent_experience'] = WorkExperience.objects.all().first()
        return context

class ProjectListView(ListView):
    model = Project
    template_name = 'code_portfolio/project_list.html'
    context_object_name = 'projects'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.annotate(project_count=Count('projects')).filter(project_count__gt=0)
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        skill_filter = self.request.GET.get('skill')
        if skill_filter:
            queryset = queryset.filter(skills__name__iexact=skill_filter)
        return queryset

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'code_portfolio/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related projects based on shared skills
        current_project = self.get_object()
        related_projects = Project.objects.filter(
            skills__in=current_project.skills.all()
        ).exclude(id=current_project.id).distinct()[:3]
        context['related_projects'] = related_projects
        return context

class AboutView(TemplateView):
    template_name = 'code_portfolio/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['work_experiences'] = WorkExperience.objects.all()
        context['education'] = Education.objects.all()
        context['certificates'] = Certificate.objects.all()
        context['skills'] = {category[0]: Skill.objects.filter(category=category[0]) 
                            for category in Skill.CATEGORY_CHOICES}
        return context

class SkillsView(ListView):
    model = Skill
    template_name = 'code_portfolio/skills.html'
    context_object_name = 'skills'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skill_categories'] = {category[0]: category[1] for category in Skill.CATEGORY_CHOICES}
        context['skills_by_category'] = {category[0]: Skill.objects.filter(category=category[0]) 
                                       for category in Skill.CATEGORY_CHOICES}
        return context

class ContactView(TemplateView):
    template_name = 'code_portfolio/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ContactForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Check for spam using the same blocked keywords from your existing site
            from django.conf import settings
            message = form.cleaned_data['message'].lower()
            subject = form.cleaned_data['subject'].lower()
            
            blocked_keywords = getattr(settings, 'BLOCKED_KEYWORDS', [])
            if any(keyword in message or keyword in subject for keyword in blocked_keywords):
                messages.error(request, "Your message appears to contain prohibited content.")
                return render(request, self.template_name, {'form': form})
            
            form.save()
            messages.success(request, "Your message has been sent. I'll get back to you soon!")
            return redirect('code_portfolio:contact')
        
        return render(request, self.template_name, {'form': form})