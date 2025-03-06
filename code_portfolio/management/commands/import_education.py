# code_portfolio/management/commands/import_education.py
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from code_portfolio.models import Education, Certificate
from django.conf import settings

class Command(BaseCommand):
    help = 'Imports education and certification data into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to import education and certifications...')
        
        # Create the education entries
        self.create_education()
        
        # Create the certificate entries
        self.create_certificates()
        
        self.stdout.write(self.style.SUCCESS('Successfully imported all education and certification data!'))
    
    def create_education(self):
        """Create education entries"""
        education_data = [
            {
                'institution': 'Virginia Commonwealth University',
                'degree': 'B.S.',
                'field_of_study': 'Biology',
                'start_date': datetime(2015, 8, 1),  # Approximate start date
                'end_date': datetime(2019, 12, 1),
                'description': 'Graduated with a Bachelor of Science in Biology. Coursework included programming for Computer Science and Engineering Majors (Python-based).'
            }
        ]
        
        for edu_data in education_data:
            education, created = Education.objects.get_or_create(
                institution=edu_data['institution'],
                degree=edu_data['degree'],
                field_of_study=edu_data['field_of_study'],
                defaults={
                    'start_date': edu_data['start_date'],
                    'end_date': edu_data['end_date'],
                    'description': edu_data['description']
                }
            )
            
            if created:
                self.stdout.write(f"Created education: {education.degree} in {education.field_of_study} from {education.institution}")
            else:
                self.stdout.write(f"Education already exists: {education.degree} in {education.field_of_study} from {education.institution}")
    
    def create_certificates(self):
        """Create certificate entries"""
        certificate_data = [
            {
                'name': 'Google IT Automation with Python Professional',
                'issuer': 'Google',
                'date_obtained': datetime(2022, 6, 1),  # Approximate date
                'description': 'Professional certificate covering Python programming, automation, troubleshooting, and debugging. Includes using Python to interact with the operating system, IT infrastructure services, and cloud computing.',
                'url': 'https://www.coursera.org/professional-certificates/google-it-automation'
            },
            {
                'name': 'Python Novice to Pythonista',
                'issuer': 'Skillsoft',
                'date_obtained': datetime(2021, 9, 1),  # Approximate date
                'description': 'Advanced Python programming certificate covering best practices, design patterns, and professional development techniques.',
                'url': ''
            },
            {
                'name': 'Programming for Computer Science & Engineering Majors I',
                'issuer': 'Virginia Commonwealth University',
                'date_obtained': datetime(2019, 5, 1),  # Approximate date
                'description': 'Python-based coursework covering programming fundamentals, data structures, and algorithms.',
                'url': ''
            }
        ]
        
        for cert_data in certificate_data:
            certificate, created = Certificate.objects.get_or_create(
                name=cert_data['name'],
                issuer=cert_data['issuer'],
                defaults={
                    'date_obtained': cert_data['date_obtained'],
                    'description': cert_data['description'],
                    'url': cert_data['url']
                }
            )
            
            if created:
                self.stdout.write(f"Created certificate: {certificate.name} from {certificate.issuer}")
            else:
                self.stdout.write(f"Certificate already exists: {certificate.name} from {certificate.issuer}")