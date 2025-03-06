# code_portfolio/management/commands/import_work_experience.py
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from code_portfolio.models import WorkExperience, Skill
from django.core.files.base import ContentFile
from django.conf import settings

class Command(BaseCommand):
    help = 'Imports work experience data into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to import work experience...')
        
        # Create the experience entries
        self.create_work_experience()
        
        self.stdout.write(self.style.SUCCESS('Successfully imported all work experience!'))
    
    def create_work_experience(self):
        """Create work experience entries"""
        experience_data = [
            {
                'company': 'INADEV',
                'position': 'SOFTWARE ENGINEER – PYTHON DEVELOPER',
                'location': 'Remote',
                'start_date': datetime(2022, 11, 1),
                'end_date': None,
                'is_current': True,
                'description': """
<ul>
    <li>Designed, developed, and implemented Python-based enterprise solutions in collaboration with a cross-functional Agile team, ensuring client requirements were met efficiently.</li>
    <li>Coordinated with team members to follow best practices, plan work, and communicate progress to clients.</li>
    <li>Supported quality development practices, including test-driven development, to ensure the reliability and robustness of software solutions.</li>
    <li>Actively participated in improving the codebase through code reviews and adherence to Agile principles.</li>
    <li>Evaluated technical effort for implementing client requirements and contributed to the creation and sizing of user stories.</li>
    <li>Contributed to system design documentation and procedures.</li>
    <li>Demonstrated proficiency in object-oriented methodologies, design patterns, and microservices architecture.</li>
</ul>
                """,
                'order': 1,
                'skills_used': ['Python', 'Django', 'Web Development', 'RESTful APIs', 'Git', 'Automation']
            },
            {
                'company': 'PPD',
                'position': 'SCIENTIST – AUTOMATION SPECIALIST',
                'location': 'Richmond, VA',
                'start_date': datetime(2022, 11, 1),
                'end_date': datetime(2023, 1, 31),
                'is_current': False,
                'description': """
<ul>
    <li>Operated and troubleshot Hamilton Star liquid handling automation platforms.</li>
    <li>Worked with other automated systems like Artel Multichannel verification systems.</li>
</ul>
                """,
                'order': 2,
                'skills_used': ['Python', 'Automation', 'Data Analysis']
            },
            {
                'company': 'PPD',
                'position': 'ASSOCIATE SCIENTIST – AUTOMATION SPECIALIST',
                'location': 'Richmond, VA',
                'start_date': datetime(2021, 9, 1),
                'end_date': datetime(2022, 11, 30),
                'is_current': False,
                'description': """
<ul>
    <li>Developed Python-Selenium based scripts to automate web application data entry, reducing errors and saving time.</li>
    <li>Created Python file system crawler to automate team member training verification.</li>
    <li>Scraped export PDFs with Python and visualized lab instrument usage data using Seaborn.</li>
    <li>Gained experience with scripting for and operating Tecan Evo liquid handlers.</li>
</ul>
                """,
                'order': 3,
                'skills_used': ['Python', 'Selenium', 'Web Automation', 'Data Visualization', 'File System Operations']
            },
            {
                'company': 'PPD',
                'position': 'ASSISTANT SCIENTIST – AUTOMATION',
                'location': 'Richmond, VA',
                'start_date': datetime(2021, 1, 1),
                'end_date': datetime(2021, 8, 31),
                'is_current': False,
                'description': """
<ul>
    <li>Created standalone graphical user interfaces (GUIs) with Python-Tkinter and PyInstaller.</li>
    <li>Developed custom Python scripts to automate complex daily sample controls calculations.</li>
    <li>Operated and troubleshot Hamilton Star liquid handling automation platforms.</li>
</ul>
                """,
                'order': 4,
                'skills_used': ['Python', 'GUI Development', 'Automation', 'Data Processing']
            },
            {
                'company': 'Virginia Commonwealth University',
                'position': 'LABORATORY SPECIALIST',
                'location': 'Richmond, VA',
                'start_date': datetime(2019, 12, 1),
                'end_date': datetime(2021, 1, 31),
                'is_current': False,
                'description': """
<ul>
    <li>Utilized Python-OpenCV library to create custom computer vision software for tracking different color rodents.</li>
    <li>Implemented Raspberry Pi and near IR PiCam with custom Python scripts to observe and record lab rodent behavior.</li>
</ul>
                """,
                'order': 5,
                'skills_used': ['Python', 'OpenCV', 'Computer Vision', 'Raspberry Pi']
            }
        ]
        
        for exp_data in experience_data:
            experience, created = WorkExperience.objects.get_or_create(
                company=exp_data['company'],
                position=exp_data['position'],
                defaults={
                    'location': exp_data['location'],
                    'start_date': exp_data['start_date'],
                    'end_date': exp_data['end_date'],
                    'is_current': exp_data['is_current'],
                    'description': exp_data['description'],
                    'order': exp_data['order']
                }
            )
            
            if created:
                # Add skills
                for skill_name in exp_data['skills_used']:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        experience.skills_used.add(skill)
                    except Skill.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Skill not found for experience: {skill_name}"))
                
                self.stdout.write(f"Created work experience: {experience.position} at {experience.company}")
            else:
                self.stdout.write(f"Work experience already exists: {experience.position} at {experience.company}")