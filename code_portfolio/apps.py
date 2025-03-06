# code_portfolio/apps.py
from django.apps import AppConfig

class CodePortfolioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'code_portfolio'
    verbose_name = 'Programming Portfolio'