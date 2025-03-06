# code_portfolio/management/commands/import_sample_projects.py
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from code_portfolio.models import Project, Skill
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files import File

class Command(BaseCommand):
    help = 'Imports sample projects into the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting to import sample projects...')
        
        # First, ensure we have the necessary skills
        self.create_skills()
        
        # Then create the projects
        self.create_projects()
        
        self.stdout.write(self.style.SUCCESS('Successfully imported all sample projects!'))
    
    def create_skills(self):
        """Create necessary skills if they don't exist"""
        skills_data = [
            # Languages
            {'name': 'Python', 'category': 'LANGUAGE', 'proficiency': 9, 'order': 1},
            {'name': 'JavaScript', 'category': 'LANGUAGE', 'proficiency': 7, 'order': 2},
            {'name': 'HTML/CSS', 'category': 'LANGUAGE', 'proficiency': 8, 'order': 3},
            
            # Frameworks
            {'name': 'Django', 'category': 'FRAMEWORK', 'proficiency': 8, 'order': 1},
            {'name': 'Flask', 'category': 'FRAMEWORK', 'proficiency': 7, 'order': 2},
            {'name': 'Bootstrap', 'category': 'FRAMEWORK', 'proficiency': 8, 'order': 3},
            {'name': 'Pandas', 'category': 'FRAMEWORK', 'proficiency': 8, 'order': 4},
            {'name': 'NumPy', 'category': 'FRAMEWORK', 'proficiency': 7, 'order': 5},
            {'name': 'Matplotlib', 'category': 'FRAMEWORK', 'proficiency': 7, 'order': 6},
            {'name': 'Seaborn', 'category': 'FRAMEWORK', 'proficiency': 7, 'order': 7},
            {'name': 'Selenium', 'category': 'FRAMEWORK', 'proficiency': 8, 'order': 8},
            {'name': 'OpenCV', 'category': 'FRAMEWORK', 'proficiency': 7, 'order': 9},
            
            # Databases
            {'name': 'MySQL', 'category': 'DATABASE', 'proficiency': 8, 'order': 1},
            {'name': 'PostgreSQL', 'category': 'DATABASE', 'proficiency': 7, 'order': 2},
            {'name': 'SQLite', 'category': 'DATABASE', 'proficiency': 7, 'order': 3},
            
            # Tools
            {'name': 'AWS S3', 'category': 'TOOL', 'proficiency': 8, 'order': 1},
            {'name': 'Git', 'category': 'TOOL', 'proficiency': 8, 'order': 2},
            {'name': 'Automation', 'category': 'TOOL', 'proficiency': 9, 'order': 3},
            {'name': 'RESTful APIs', 'category': 'TOOL', 'proficiency': 7, 'order': 4},
            {'name': 'Raspberry Pi', 'category': 'TOOL', 'proficiency': 7, 'order': 5},
            {'name': 'Data Analysis', 'category': 'TOOL', 'proficiency': 8, 'order': 6},
            {'name': 'Data Visualization', 'category': 'TOOL', 'proficiency': 7, 'order': 7},
            {'name': 'GUI Development', 'category': 'TOOL', 'proficiency': 6, 'order': 8},
            {'name': 'OCR', 'category': 'TOOL', 'proficiency': 6, 'order': 9},
            {'name': 'SEO', 'category': 'TOOL', 'proficiency': 7, 'order': 10},
            
            # Concepts
            {'name': 'Web Development', 'category': 'CONCEPT', 'proficiency': 8, 'order': 1},
            {'name': 'Computer Vision', 'category': 'CONCEPT', 'proficiency': 7, 'order': 2},
            {'name': 'Web Automation', 'category': 'CONCEPT', 'proficiency': 8, 'order': 3},
            {'name': 'Data Processing', 'category': 'CONCEPT', 'proficiency': 8, 'order': 4},
            {'name': 'File System Operations', 'category': 'CONCEPT', 'proficiency': 7, 'order': 5},
        ]
        
        for skill_data in skills_data:
            skill, created = Skill.objects.get_or_create(
                name=skill_data['name'],
                defaults={
                    'category': skill_data['category'],
                    'proficiency': skill_data['proficiency'],
                    'order': skill_data['order']
                }
            )
            
            if created:
                self.stdout.write(f"Created skill: {skill.name}")
            else:
                self.stdout.write(f"Skill already exists: {skill.name}")
    
    def create_projects(self):
        """Create the sample projects"""
        projects_data = [
            {
                'title': 'Photography Portfolio & Booking System',
                'slug': 'photography-portfolio-booking-system',
                'description': 'Full-stack photography portfolio and client booking platform built with Django, featuring automated gallery delivery, integrated booking system, and custom CMS.',
                'content': """
## Project Overview

The Photography Portfolio & Booking System is a comprehensive web application designed for professional photographers to showcase their work, manage client bookings, and streamline their workflow.

### Key Features

#### Portfolio Showcase
- Responsive gallery system with category filtering
- High-resolution image support with dynamic compression
- Lazy loading and image optimization for performance
- SEO-friendly URLs and metadata

#### Client Booking System
- Interactive availability calendar
- Custom booking form with session type selection
- Automated email confirmations
- Client dashboard for booking management

#### Client Gallery Delivery
- Secure, password-protected client galleries
- Automated image processing and upload
- Direct download and favorite selection for clients
- Social sharing integration

#### Content Management System
- Custom Django admin interface for content management
- Blog with rich text editing
- Testimonial and review management
- SEO optimization tools

### Technical Details

The application is built using Django with a PostgreSQL database. Images are stored and served via AWS S3 for performance and scalability. The front-end uses Bootstrap for responsive design with custom JavaScript for interactive elements.

#### Technology Stack:
- Django 4.0
- PostgreSQL
- AWS S3 for image storage
- Bootstrap 5
- jQuery and custom JavaScript
- Django CKEditor for rich text editing
- Django Storages for AWS integration
- Custom middleware for client session management

#### API Integrations:
- Instagram API for social feed integration
- Google Analytics for visitor tracking
- Mailchimp for newsletter management
- Meta Pixel for conversion tracking

### Development Process

The development followed a feature-driven approach, starting with core portfolio functionality and gradually expanding to include booking and client gallery features. Test-driven development practices were implemented to ensure reliability across all components.

### Challenges and Solutions

**Challenge**: Handling large image uploads and processing
**Solution**: Implemented asynchronous image processing using Django signals and AWS Lambda for background image optimization

**Challenge**: SEO optimization for photography content
**Solution**: Implemented Schema.org structured data, custom metadata, and automatic XML sitemap generation

**Challenge**: Secure client gallery delivery
**Solution**: Developed a custom authentication system with time-limited access tokens and watermarking capabilities
                """,
                'github_url': 'https://github.com/stephenlawson/photography-portfolio',
                'live_url': 'https://stephen.photography',
                'date_created': datetime(2023, 5, 15),
                'is_featured': True,
                'order': 1,
                'skills': ['Python', 'Django', 'MySQL', 'AWS S3', 'HTML/CSS', 'JavaScript', 'Bootstrap', 'RESTful APIs', 'SEO']
            },
            {
                'title': 'Laboratory Automation Framework',
                'slug': 'lab-automation-framework',
                'description': 'Python-based automation framework for laboratory workflows, increasing efficiency and reducing manual errors in research environments.',
                'content': """
## Project Overview

The Laboratory Automation Framework is a comprehensive Python-based solution designed to automate common laboratory workflows, data processing, and reporting tasks in research environments. Drawing from my experience in laboratory settings, this project addresses key challenges faced by researchers in managing complex experimental data.

### Key Features

#### Instrument Integration
- Automated data collection from Hamilton Star liquid handlers
- Integration with Artel Multichannel verification systems
- Standardized API for connecting to various lab instruments

#### Data Processing Pipeline
- Automated parsing of experimental output files
- Statistical analysis with outlier detection
- Data normalization and transformation
- Result visualization and reporting

#### Workflow Automation
- Experiment scheduling and tracking
- Reagent inventory management
- Sample tracking and chain of custody
- Quality control monitoring

#### Reporting System
- Customizable report templates
- Automated PDF generation
- Interactive data visualizations
- Export options for various formats (CSV, Excel, JSON)

### Technical Implementation

#### Core Technologies
- Python 3.9
- Pandas for data manipulation
- NumPy and SciPy for numerical computations
- Matplotlib and Seaborn for data visualization
- Flask for web interface components
- SQLite for local data storage
- PyInstaller for creating standalone executables

#### Architecture
The framework follows a modular architecture with clear separation of concerns:
- Instrument connectors handle device-specific communication
- Data processors transform raw data into structured formats
- Analysis modules perform statistical calculations
- Visualization components generate plots and charts
- Reporting engine produces formatted output documents

### Development Process

This project was developed iteratively, starting with core functionality for a specific instrument (Hamilton Star) and gradually expanding to support additional devices and workflows. Automated testing was implemented to ensure reliability across different laboratory environments.

### Impact

The Laboratory Automation Framework has significantly improved efficiency in laboratory operations:
- Reduced manual data entry errors by approximately 95%
- Decreased data processing time by 85% compared to manual methods
- Standardized reporting across different experiments
- Enabled reproducible analysis workflows
- Improved traceability for regulatory compliance

### Future Enhancements

- Machine learning integration for predictive quality control
- Cloud-based storage and sharing options
- Mobile application for remote monitoring
- Integration with electronic laboratory notebooks (ELNs)
                """,
                'github_url': 'https://github.com/stephenlawson/lab-automation',
                'live_url': '',
                'date_created': datetime(2022, 8, 10),
                'is_featured': True,
                'order': 2,
                'skills': ['Python', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Flask', 'Automation', 'Data Analysis']
            },
            {
                'title': 'Computer Vision Rodent Tracking System',
                'slug': 'computer-vision-rodent-tracking',
                'description': 'Custom computer vision solution using Python-OpenCV to automatically track rodent movement and behavior in laboratory settings, enabling efficient data collection for research studies.',
                'content': """
## Project Overview

The Computer Vision Rodent Tracking System is a specialized tool designed to automate the tracking and analysis of rodent behavior in laboratory settings. Built using Python and OpenCV, this system eliminates the need for manual observation and data collection, significantly improving research efficiency and data accuracy.

### Key Features

#### Real-time Tracking
- Multi-animal tracking capability
- Color-based identification for different subjects
- Movement path visualization
- Zone entry/exit detection

#### Behavior Analysis
- Automatic detection of common behaviors (resting, grooming, exploration)
- Social interaction monitoring
- Activity level quantification
- Posture and orientation analysis

#### Environmental Integration
- Near-IR illumination compatibility for dark cycle recording
- Integration with Raspberry Pi cameras for distributed monitoring
- Low-light condition optimization
- Time-synchronized environmental data recording

#### Data Analysis & Export
- Comprehensive metrics calculation (distance traveled, time in zones, etc.)
- Heat map generation of movement patterns
- Statistical summary reports
- Data export to CSV for further analysis

### Technical Implementation

#### Hardware Components
- Raspberry Pi 4 with PiCamera
- Near-IR LED illumination array
- Custom 3D-printed camera mount system
- Dedicated monitoring station

#### Software Architecture
- Python 3.8 core application
- OpenCV 4.5 for image processing and analysis
- NumPy for numerical operations
- Pandas for data management
- Matplotlib and Seaborn for visualization
- SQLite for session storage

#### Tracking Algorithm
The system employs a combination of techniques:
1. Background subtraction to isolate moving objects
2. Color thresholding for subject identification
3. Contour detection and analysis for posture estimation
4. Kalman filtering for tracking prediction and occlusion handling

### Development Process

This project evolved through several iterations based on real laboratory needs. Starting with basic motion detection, it gradually incorporated more sophisticated tracking algorithms and behavior analysis capabilities. Regular feedback from researchers guided feature development and refinement.

### Challenges and Solutions

**Challenge**: Distinguishing between similar-colored animals
**Solution**: Implemented a combination of color thresholding and spatial positioning tracking

**Challenge**: Maintaining tracking during occlusions or close interactions
**Solution**: Applied Kalman filtering to predict movement and recover tracking after occlusion events

**Challenge**: Low-light recording conditions
**Solution**: Developed near-IR illumination system and camera settings optimization

### Results and Impact

The system has been successfully deployed in several behavioral neuroscience studies, resulting in:
- 90% reduction in manual observation time
- Increased data granularity (30 fps vs. spot sampling)
- Improved consistency in behavior classification
- Novel insights into subtle movement patterns
- Enhanced reproducibility of behavioral experiments

### Future Directions
- Deep learning integration for more sophisticated behavior recognition
- 3D tracking using multiple camera perspectives
- Cloud-based data storage and analysis
- Web interface for remote monitoring
                """,
                'github_url': 'https://github.com/stephenlawson/rodent-tracking',
                'live_url': '',
                'date_created': datetime(2021, 3, 20),
                'is_featured': False,
                'order': 3,
                'skills': ['Python', 'OpenCV', 'Computer Vision', 'Raspberry Pi', 'NumPy', 'Data Visualization']
            },
            {
                'title': 'Web Data Entry Automation Tool',
                'slug': 'web-data-entry-automation',
                'description': 'Python-Selenium based automation solution that streamlines repetitive data entry tasks, significantly reducing processing time and human error in laboratory information systems.',
                'content': """
## Project Overview

The Web Data Entry Automation Tool is a specialized Python application designed to automate repetitive data entry tasks in web-based laboratory information systems. This solution addresses the significant time sink and error potential in manual data transcription from laboratory instruments to web applications.

### Problem Statement

Laboratory technicians often spend hours manually transferring data from instrument outputs to various web-based systems. This process is:
- Time-consuming
- Error-prone
- Mentally taxing
- A poor use of skilled personnel

### Solution

I developed a robust automation system using Python and Selenium WebDriver to:
1. Extract data from laboratory instrument exports (CSV, Excel, and text formats)
2. Intelligently parse and validate the extracted information
3. Automatically navigate through web application interfaces
4. Enter data into the appropriate fields with validation checks
5. Generate comprehensive logs and reports of all actions

### Key Features

#### Data Extraction System
- Support for multiple input formats (CSV, Excel, TEXT, PDF)
- Template-based extraction for consistent formatting
- Data validation with configurable rules
- Error handling for inconsistent source formats

#### Web Automation Engine
- Robust Selenium-based navigation and interaction
- Configurable wait timings for dynamic content
- Element identification via multiple methods (XPath, CSS, ID)
- Error recovery mechanisms for unexpected page states

#### Validation & Quality Control
- Pre-submission data validation
- Checkpoint verification during entry process
- Post-submission verification
- Comprehensive logging and audit trail

#### User Interface
- Simple configuration interface for non-technical users
- Progress monitoring during automation runs
- Detailed reporting of completed actions
- Error alerts with suggested resolutions

### Technical Implementation

#### Technology Stack
- Python 3.9
- Selenium WebDriver
- Pandas for data manipulation
- PyQt5 for desktop interface
- Logging module for audit trails
- ConfigParser for settings management

#### Architecture
The application follows a modular design with:
- Data extractors for different input formats
- Web action modules for specific web applications
- Controller logic to orchestrate the process
- Configuration system for customization
- Reporting engine for output generation

### Impact and Results

This automation tool has delivered significant benefits:
- Reduced data entry time by 95% (from hours to minutes)
- Decreased error rates from approximately 3% to less than 0.1%
- Freed up approximately 15-20 hours per week of technician time
- Improved data consistency across systems
- Enhanced audit trail for regulatory compliance

### Challenges and Solutions

**Challenge**: Dynamic web elements that change position or ID
**Solution**: Implemented multiple identification strategies and fallback mechanisms

**Challenge**: Handling unexpected pop-ups and alerts
**Solution**: Created a comprehensive exception handling system with recovery procedures

**Challenge**: Making the tool accessible to non-technical users
**Solution**: Developed a simple GUI with clear configuration options and visual feedback

### Future Enhancements

- Machine learning for improved data extraction from unstructured sources
- Browser-based extension version for easier deployment
- API integration for direct system-to-system communication
- Remote execution scheduling capabilities
                """,
                'github_url': 'https://github.com/stephenlawson/data-entry-automation',
                'live_url': '',
                'date_created': datetime(2022, 1, 15),
                'is_featured': False,
                'order': 4,
                'skills': ['Python', 'Selenium', 'Web Automation', 'Data Processing', 'GUI Development']
            },
            {
                'title': 'Team Training Verification System',
                'slug': 'training-verification-system',
                'description': 'Automated file system crawler built with Python to streamline compliance verification for team member training, reducing manual effort and ensuring regulatory requirements are met.',
                'content': """
## Project Overview

The Team Training Verification System is an automated solution developed to address the challenge of tracking and verifying employee training compliance in regulated environments. This Python-based tool eliminates manual verification processes by automatically crawling file systems, identifying training documentation, and generating compliance reports.

### Problem Context

In regulated industries like healthcare and pharmaceuticals, maintaining up-to-date training records is critical for compliance and audit purposes. The manual process of verifying training status was:
- Time-intensive (8+ hours per week)
- Error-prone due to human oversight
- Difficult to scale with team growth
- Inconsistent in approach between verifiers

### Solution Architecture

I developed a comprehensive file system crawler that:
1. Recursively scans network directories containing training documentation
2. Identifies and extracts key information using pattern matching and OCR
3. Verifies completion status against requirements databases
4. Generates status reports and flags expired or missing certifications
5. Provides audit-ready documentation of the verification process

### Key Features

#### Intelligent Document Processing
- Support for multiple document formats (PDF, DOCX, JPG, PNG)
- OCR capability for scanned document processing
- Pattern recognition for certificate identification
- Natural language processing for extracting completion dates

#### Compliance Verification Engine
- Rule-based validation of training requirements
- Expiration date tracking and alerting
- Cross-reference with HR databases for employee information
- Historical record maintenance for audit trails

#### Reporting System
- Automated weekly compliance summaries
- Individual training status reports
- Expiration forecasting (30/60/90 day warnings)
- Export capabilities in multiple formats (PDF, Excel, HTML)

#### Administrative Interface
- Web-based dashboard for compliance monitoring
- Configuration panel for requirement management
- User management for access control
- Audit log viewing and export

### Technical Implementation

#### Core Technologies
- Python 3.8 for main application logic
- PyPDF2 and Tesseract OCR for document processing
- SQLite for local data storage
- Flask for web interface components
- Pandas for data manipulation and reporting
- Schedule library for automated verification runs

#### System Architecture
The system follows a layered approach:
- Document crawler and processor layer
- Data extraction and interpretation layer
- Verification and validation logic layer
- Reporting and notification engine
- Web-based user interface

### Development Process

The project was developed following an agile methodology:
1. Initial proof of concept focused on PDF processing
2. Expanded to include additional document formats
3. Added verification logic and database integration
4. Developed reporting capabilities
5. Created web dashboard for management

### Results and Impact

The Training Verification System delivered significant operational improvements:
- Reduced verification time from 8+ hours to under 30 minutes per week
- Improved compliance rate from 92% to 99.5%
- Early notification of expiring certifications reduced lapsed training by 87%
- Provided audit-ready reports that successfully passed multiple regulatory inspections
- Freed up approximately 400 hours per year of administrative time

### Challenges and Solutions

**Challenge**: Inconsistent document formatting from different training systems
**Solution**: Implemented flexible pattern matching and machine learning classification

**Challenge**: Access to restricted network directories
**Solution**: Developed a secure agent-based architecture with appropriate permissions

**Challenge**: Integration with existing HR systems
**Solution**: Created configurable connectors for various database formats and APIs

### Future Enhancements

- Mobile application for on-the-go compliance checking
- Integration with learning management systems for automatic updates
- Enhanced analytics for training effectiveness measurement
- Automated enrollment in required training based on role changes
                """,
                'github_url': 'https://github.com/stephenlawson/training-verification',
                'live_url': '',
                'date_created': datetime(2022, 4, 5),
                'is_featured': False,
                'order': 5,
                'skills': ['Python', 'File System Operations', 'Automation', 'OCR', 'Data Analysis']
            },
        ]
        
        # Create placeholder images directory if it doesn't exist
        placeholder_dir = os.path.join(settings.MEDIA_ROOT, 'code_portfolio', 'placeholders')
        os.makedirs(placeholder_dir, exist_ok=True)
        
        # Create each project
        for project_data in projects_data:
            # Check if project already exists
            if Project.objects.filter(slug=project_data['slug']).exists():
                self.stdout.write(f"Project already exists: {project_data['title']}")
                continue
            
            # Create the project
            project = Project(
                title=project_data['title'],
                slug=project_data['slug'],
                description=project_data['description'],
                content=project_data['content'],
                github_url=project_data['github_url'],
                live_url=project_data['live_url'],
                date_created=project_data['date_created'],
                is_featured=project_data['is_featured'],
                order=project_data['order'],
            )
            
            # Create a simple colored placeholder image
            placeholder_filename = f"{slugify(project_data['title'])}.jpg"
            placeholder_path = os.path.join(placeholder_dir, placeholder_filename)
            
            # If we have a real placeholder image, use that
            if os.path.exists(placeholder_path):
                with open(placeholder_path, 'rb') as f:
                    project.featured_image.save(placeholder_filename, File(f), save=False)
            else:
                # Otherwise create a simple placeholder content
                import io
                from PIL import Image, ImageDraw, ImageFont
                
                # Create a colored image with the project title
                img = Image.new('RGB', (800, 600), color=(73, 109, 137))
                d = ImageDraw.Draw(img)
                # Try to use a font, fall back to default if not available
                try:
                    font = ImageFont.truetype("arial.ttf", 36)
                except IOError:
                    font = ImageFont.load_default()
                
                d.text((400, 300), project_data['title'], fill=(255, 255, 255), anchor="mm", font=font)
                
                # Save to BytesIO object
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                
                # Save to model
                project.featured_image.save(placeholder_filename, ContentFile(img_io.read()), save=False)
            
            # Save the project to get an ID
            project.save()
            
            # Add skills
            for skill_name in project_data['skills']:
                try:
                    skill = Skill.objects.get(name=skill_name)
                    project.skills.add(skill)
                except Skill.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Skill not found: {skill_name}"))
            
            self.stdout.write(f"Created project: {project.title}")