# Django Photography Portfolio

A full-stack photography portfolio and client management system built with Django, featuring automated client galleries, integrated booking system, and a custom CMS.

## 🌟 Live Site

Visit the live site at [stephen.photography](https://stephen.photography)

## ✨ Features

### Portfolio Showcase
- Responsive gallery system with category filtering
- High-resolution image support with dynamic compression
- Lazy loading and image optimization for performance
- SEO-friendly URLs and metadata

### Client Booking System
- Interactive availability calendar
- Custom booking form with session type selection
- Automated email confirmations
- Client dashboard for booking management

### Client Gallery Delivery
- Secure, password-protected client galleries
- Automated image processing and upload
- Direct download and favorite selection for clients
- Social sharing integration

### Content Management System
- Custom Django admin interface for content management
- Blog with rich text editing
- Testimonial and review management
- SEO optimization tools

## 🛠️ Technology Stack

- **Backend**: Django 4.0
- **Database**: PostgreSQL
- **Storage**: AWS S3
- **Frontend**: Bootstrap 5, jQuery, custom JavaScript
- **Content Editing**: Django CKEditor
- **Cloud Integration**: Django Storages with AWS S3
- **Email**: SMTP via Gmail

## 🔌 API Integrations

- Instagram API for social feed integration
- Google Analytics for visitor tracking
- Meta Pixel for conversion tracking
- Google Maps for location displays

## 📦 Project Structure

The project consists of three main Django apps:
1. **photo_app** - Core portfolio functionality
2. **photo_blog** - Blog and content features
3. **django_portfolio** - Main project configuration

## 🚀 Development

### Prerequisites
- Python 3.9+
- PostgreSQL
- AWS S3 account
- Node.js and npm for frontend assets

### Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv env`
3. Activate the environment: `source env/bin/activate` (Linux/Mac) or `env\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables (see .env.example)
6. Run migrations: `python manage.py migrate`
7. Create a superuser: `python manage.py createsuperuser`
8. Run the server: `python manage.py runserver`

## 🔧 Configuration

The project uses a JSON configuration file stored in `/etc/config.json` with the following structure:

```json
{
  "SECRET_KEY": "your-secret-key",
  "ENGINE": "django.db.backends.postgresql",
  "PORT_SITE": "your-db-name",
  "AWS_HOST": "your-aws-host",
  "AWS_PORT": "your-port",
  "AWS_USERNAME": "your-username",
  "AWS_PASSWORD": "your-password",
  "DEFAULT_FILE_STORAGE": "storages.backends.s3boto3.S3Boto3Storage",
  "AWS_SECRET_ACCESS_KEY": "your-aws-secret",
  "AWS_ACCESS_KEY_ID": "your-aws-key-id",
  "AWS_STORAGE_BUCKET_NAME": "your-bucket-name",
  "EMAIL_HOST_PASSWORD": "your-email-password",
  "EMAIL_HOST_USER": "your-email@example.com",
  "RECAPTCHA_PUBLIC_KEY": "your-recaptcha-public-key",
  "RECAPTCHA_PRIVATE_KEY": "your-recaptcha-private-key",
  "INSTA_ACCESS_TOKEN": "your-instagram-token",
  "GOOGLE_API_KEY": "your-google-api-key",
  "GOOGLE_PLACE_ID": "your-google-place-id"
}
```

## 🌐 Deployment

The site is currently deployed on a VPS using:
- Nginx as a reverse proxy
- Gunicorn as a WSGI server
- Supervisor for process management
- Let's Encrypt for SSL certificates

## 📝 License

This project is proprietary and is not licensed for public use or modification.

## 👤 Author

Stephen Lawson
- [GitHub](https://github.com/stephenlawson)
- [LinkedIn](https://linkedin.com/in/stephen-lawson-stl/)
- [Photography Portfolio](https://stephen.photography)
- [Programming Portfolio](https://code.stephen.photography)