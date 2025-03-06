# photo_app/management/commands/add_alt_text.py
from django.core.management.base import BaseCommand
from photo_app.models import Photo4, ClientGallery, Category
import os


class Command(BaseCommand):
    help = (
        "Adds SEO-friendly alt text to all photos based on their gallery and category"
    )

    def handle(self, *args, **kwargs):
        photos = Photo4.objects.select_related("gallery", "gallery__category").all()
        updated_count = 0

        for photo in photos:
            try:
                # Get context information
                gallery_name = photo.gallery.name
                category_name = photo.gallery.category.get_name_display()
                file_name = os.path.basename(photo.image.name)

                # Build descriptive alt text
                alt_text = f"Richmond {category_name} photography - {gallery_name} by Stephen Lawson Photography"

                # Add any special descriptors based on orientation or filename
                if photo.orientation == "portrait":
                    alt_text = f"Portrait style {alt_text.lower()}"
                elif photo.orientation == "landscape":
                    alt_text = f"Landscape {alt_text.lower()}"

                # Save alt text to the photo
                photo.alt_text = alt_text
                photo.save(update_fields=["alt_text"])

                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Added alt text to: {file_name}"))

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing photo {photo.id}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Successfully added alt text to {updated_count} photos")
        )
