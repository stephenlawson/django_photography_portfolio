from django.test import TestCase, Client, override_settings
from django.urls import reverse, resolve
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.core import mail
from django.utils import timezone
from photo_app.models import (
    Photo3, Comment, InstagramPost, Review, Contact, 
    Category, ClientGallery, Photo4, ServiceCategory, 
    Service, Event, AccessRequest, PageContent
)
from photo_app.forms import ContactForm, GalleryAccessRequestForm
from photo_blog.models import BlogPost
import json
from datetime import date, datetime
from django.core.files.storage import default_storage
from unittest.mock import patch, MagicMock

class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='portrait',
            intro_text='Test intro text'
        )
        
        # Create test gallery
        self.gallery = ClientGallery.objects.create(
            category=self.category,
            name='Test Gallery',
            date=date.today()
        )
        
        # Create test event
        self.event = Event.objects.create(
            name='Test Event',
            date=date.today()
        )

    def test_category_model(self):
        self.assertEqual(str(self.category), 'Portraits')
        self.assertEqual(self.category.intro_text, 'Test intro text')

    def test_client_gallery_model(self):
        self.assertEqual(str(self.gallery), 'Test Gallery (Portraits)')
        self.assertTrue(self.gallery.slug)

    def test_photo4_model(self):
        photo = Photo4.objects.create(
            gallery=self.gallery,
            image='test.jpg'
        )
        self.assertEqual(str(photo), 'Photo test.jpg - Gallery Test Gallery (Portraits)')

    def test_service_category_model(self):
        service_cat = ServiceCategory.objects.create(
            name='wedding',
            display_name='Wedding Photography',
            base_price='From $2000'
        )
        self.assertEqual(str(service_cat), 'Wedding Photography')

    def test_service_model(self):
        service_cat = ServiceCategory.objects.create(
            name='wedding',
            display_name='Wedding Photography'
        )
        service = Service.objects.create(
            category=service_cat,
            name='Basic Package',
            description='Test description',
            base_price=2000.00
        )
        self.assertEqual(str(service), 'wedding - Basic Package')

    def test_event_model(self):
        self.assertEqual(str(self.event), f'Test Event ({date.today()})')
        self.assertTrue(self.event.slug)

    def test_access_request_model(self):
        request = AccessRequest.objects.create(
            name='Test User',
            email='test@example.com',
            event=self.event
        )
        self.assertEqual(
            str(request),
            f'Access Request from Test User for Test Event'
        )

class FormTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(
            name='Test Event',
            date=date.today()
        )

    def test_contact_form_valid(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+12125552368',
            'service': 'Wedding',
            'date': date.today(),
            'location': 'Test Location',
            'additional_info': 'Test info'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_invalid(self):
        form_data = {
            'first_name': '',  # Required field
            'email': 'invalid-email',  # Invalid email
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)
        self.assertIn('email', form.errors)

    def test_gallery_access_form_valid(self):
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'event': self.event.id,
            'comments': 'Test comment'
        }
        form = GalleryAccessRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_gallery_access_form_duplicate_email(self):
        # Create initial request
        AccessRequest.objects.create(
            name='John Doe',
            email='john@example.com',
            event=self.event
        )
        
        # Try to submit same email for same event
        form_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'event': self.event.id
        }
        form = GalleryAccessRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test category and gallery
        self.category = Category.objects.create(
            name='portrait',
            intro_text='Test intro text'
        )
        self.gallery = ClientGallery.objects.create(
            category=self.category,
            name='Test Gallery',
            date=date.today()
        )

    def test_portfolio_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_app/index.html')

    def test_gallery_list_view(self):
        response = self.client.get(
            reverse('gallery_list', args=[self.category.name])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_app/gallery_list.html')
        self.assertContains(response, self.gallery.name)

    def test_photo_gallery_view(self):
        response = self.client.get(
            reverse('photo_gallery', args=[self.gallery.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_app/photo_gallery.html')

    # @patch('photo_app.views.send_mail')
    # def test_contact_view_submission(self, mock_send_mail):
    #     form_data = {
    #         'first_name': 'John',
    #         'last_name': 'Doe',
    #         'email': 'john@example.com',
    #         'phone': '+12125552368',
    #         'service': 'Wedding',
    #         'date': date.today(),
    #         'location': 'Test Location',
    #         'additional_info': 'Test info'
    #     }
    #     response = self.client.post(reverse('contact'), form_data)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, '/form-received')
    #     mock_send_mail.assert_called_once()

    def test_gallery_access_request_view(self):
        response = self.client.get(reverse('gallery_access_request'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_app/gallery_access_request.html')

class BlogTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.blog_post = BlogPost.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user,
            active=True
        )

    def test_blog_list_view(self):
        response = self.client.get(reverse('photo_blog:photo_blogs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_blog/post_list.html')
        self.assertContains(response, self.blog_post.title)

    def test_blog_detail_view(self):
        response = self.client.get(
            reverse('photo_blog:photo_blog', args=[self.blog_post.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'photo_blog/post_detail.html')
        self.assertContains(response, self.blog_post.title)

    def test_blog_model_methods(self):
        self.assertEqual(
            self.blog_post.get_meta_title(),
            'Test Post | Stephen Lawson Photography Blog'
        )
        self.assertEqual(
            self.blog_post.get_meta_description(),
            'Read about Test Post on the Stephen Lawson Photography blog.'
        )

class AdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.client.login(username='admin', password='adminpass123')

    def test_admin_photo_gallery_list(self):
        response = self.client.get(reverse('admin:photo_app_clientgallery_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_blog_post_list(self):
        response = self.client.get(reverse('admin:photo_blog_blogpost_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_admin_category_list(self):
        response = self.client.get(reverse('admin:photo_app_category_changelist'))
        self.assertEqual(response.status_code, 200)

@override_settings(MEDIA_ROOT='test_media/')
class FileUploadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Create test category and gallery
        self.category = Category.objects.create(name='portrait')
        self.gallery = ClientGallery.objects.create(
            category=self.category,
            name='Test Gallery',
            date=date.today()
        )

    def tearDown(self):
        # Clean up uploaded files
        import shutil
        try:
            shutil.rmtree('test_media/')
        except FileNotFoundError:
            pass

    @patch('photo_app.views.Image')
    def test_photo_upload(self, mock_image):
        # Mock PIL Image
        mock_img = MagicMock()
        mock_img.size = (800, 600)
        mock_img.mode = 'RGB'
        mock_image.open.return_value = mock_img

        # Create test image file
        image_file = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

        response = self.client.post(
            reverse('upload_photos'),
            {
                'gallery': self.gallery.id,
                'images': [image_file]
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Photo4.objects.filter(gallery=self.gallery).exists())

class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

    # def test_csrf_protection(self):
    #     # Test that CSRF token is required for forms
    #     response = self.client.post(reverse('contact'), {})
    #     self.assertEqual(response.status_code, 403)

    def test_xss_protection(self):
        # Test that XSS content is escaped
        malicious_content = '<script>alert("XSS")</script>'
        response = self.client.post(
            reverse('contact'),
            {
                'first_name': malicious_content,
                'email': 'test@example.com'
            },
            follow=True
        )
        self.assertNotContains(response, malicious_content, html=True)

class ErrorHandlingTests(TestCase):
    def test_404_handler(self):
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'errors/404.html')

    def test_403_handler(self):
        # Test accessing protected view without authentication
        response = self.client.get(reverse('upload_photos'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

class SitemapTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create test data
        self.category = Category.objects.create(
            name='portrait',
            intro_text='Test intro text'
        )
        
        self.gallery = ClientGallery.objects.create(
            category=self.category,
            name='Test Gallery',
            date=date.today(),
            slug='test-gallery'
        )
        
        self.service_category = ServiceCategory.objects.create(
            name='wedding',
            display_name='Wedding Photography'
        )
        
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='Test content',
            active=True,
            author=self.user,
            created_at=timezone.now()
        )

    def test_sitemap_xml(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')
        
        # Check if our test objects are in the sitemap
        self.assertContains(response, self.gallery.slug)
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.service_category.name)
        self.assertContains(response, self.blog_post.slug)

    def test_static_sitemap(self):
        from photo_app.sitemap import StaticViewSitemap
        sitemap = StaticViewSitemap()
        urls = sitemap.items()
        
        # Check if important static pages are included
        self.assertIn('index', urls)
        self.assertIn('services', urls)
        self.assertIn('contact', urls)
        
        # Test location method
        self.assertEqual(sitemap.location('index'), '/')

    def test_gallery_sitemap(self):
        from photo_app.sitemap import GallerySitemap
        sitemap = GallerySitemap()
        items = sitemap.items()
        
        self.assertIn(self.gallery, items)
        self.assertEqual(
            sitemap.location(self.gallery),
            f'/gallery/{self.gallery.slug}/'
        )

    def test_blog_sitemap(self):
        from photo_app.sitemap import BlogSitemap
        sitemap = BlogSitemap()
        items = sitemap.items()
        
        self.assertIn(self.blog_post, items)
        self.assertEqual(
            sitemap.location(self.blog_post),
            f'/photo_blog/{self.blog_post.slug}/'
        )
        self.assertEqual(sitemap.lastmod(self.blog_post), self.blog_post.created_at)

class SEOTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create test data
        self.category = Category.objects.create(
            name='portrait',
            intro_text='Test intro text'
        )
        
        self.gallery = ClientGallery.objects.create(
            category=self.category,
            name='Test Gallery',
            date=date.today(),
            gallery_text='Test gallery description'
        )
        
        self.blog_post = BlogPost.objects.create(
            title='Test Blog Post',
            content='Test content',
            meta_title='Custom Meta Title',
            meta_description='Custom meta description for SEO',
            meta_keywords='photography, test, blog',
            active=True
        )
        
        self.page_content = PageContent.objects.create(
            page_id='index',
            title='Home Page',
            meta_description='Welcome to our photography site',
            meta_keywords='photography, portraits, weddings'
        )

    def test_meta_tags(self):
        # Test homepage meta tags
        response = self.client.get(reverse('index'))
        self.assertContains(response, '<meta name="description"')
        self.assertContains(response, '<meta name="keywords"')
        self.assertContains(response, '<link rel="canonical"')
        
        # Test blog post meta tags
        response = self.client.get(
            reverse('photo_blog:photo_blog', args=[self.blog_post.slug])
        )
        self.assertContains(response, 'Custom Meta Title')
        self.assertContains(response, 'Custom meta description for SEO')
        self.assertContains(response, 'photography, test, blog')

    # def test_og_tags(self):
    #     # Test Open Graph tags
    #     response = self.client.get(
    #         reverse('photo_gallery', args=[self.gallery.slug])
    #     )
    #     self.assertContains(response, '<meta property="og:title"')
    #     self.assertContains(response, '<meta property="og:description"')
    #     self.assertContains(response, '<meta property="og:url"')
    #     self.assertContains(response, '<meta property="og:type"')

    def test_schema_markup(self):
        # Test JSON-LD schema markup
        response = self.client.get(reverse('index'))
        self.assertContains(response, '@context": "https://schema.org')
        self.assertContains(response, '"@type": "PhotographyBusiness"')

    def test_robots_txt(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/plain')
        self.assertContains(response, 'Sitemap: ')
        self.assertContains(response, 'Allow: /')

    def test_url_patterns(self):
        # Test SEO-friendly URL patterns
        self.assertTrue(self.gallery.slug)
        self.assertFalse('-' in self.category.name)  # Categories should be clean
        self.assertTrue(self.blog_post.slug)
        
        # Test that URLs are properly formed
        response = self.client.get(f'/gallery/{self.gallery.slug}/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f'/category/{self.category.name}/')
        self.assertEqual(response.status_code, 200)

    def test_canonical_urls(self):
        # Test canonical URLs are properly set
        response = self.client.get(reverse('index'))
        self.assertContains(response, '<link rel="canonical"')
        
        # Test blog post canonical URL
        response = self.client.get(
            reverse('photo_blog:photo_blog', args=[self.blog_post.slug])
        )
        self.assertContains(response, '<link rel="canonical"')
        
        # Test gallery canonical URL
        response = self.client.get(
            reverse('photo_gallery', args=[self.gallery.slug])
        )
        self.assertContains(response, '<link rel="canonical"')

