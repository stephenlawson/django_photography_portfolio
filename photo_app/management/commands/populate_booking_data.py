from django.core.management.base import BaseCommand
from photo_app.models import ServiceCategory, Service, AddOn
from decimal import Decimal


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Get or create Family category
        family_cat, _ = ServiceCategory.objects.get_or_create(
            name="family",
            defaults={
                "display_name": "Family Photography",
                "intro_text": "Capture precious family moments with professional photography sessions",
                "base_price": "From $200",
                "duration": "1-3 hours",
                "order": 5,
            },
        )

        # Clean up any existing services
        Service.objects.filter(category=family_cat).delete()

        # Basic Family Package
        basic_family = Service.objects.create(
            category=family_cat,
            name="Classic Family Session",
            description="""Perfect for small families. Includes:
           • 1 hour session
           • One outdoor location
           • One outfit
           • 25-30 edited photos
           • Online gallery delivery
           • Personal printing rights
           • Up to 5 people""",
            base_price=Decimal("200.00"),
            duration="1 hr",
            order=1,
        )

        # Extended Family Package
        extended_family = Service.objects.create(
            category=family_cat,
            name="Extended Family Session",
            description="""Ideal for larger families or multiple generations. Includes:
           • 2 hour session
           • One location
           • Outfit change opportunity
           • 40-50 edited photos
           • Group and individual family combinations
           • Online gallery delivery
           • Personal printing rights
           • Up to 10 people""",
            base_price=Decimal("300.00"),
            duration="2 hr",
            order=2,
        )

        # Premium Family Package
        premium_family = Service.objects.create(
            category=family_cat,
            name="Premium Family Experience",
            description="""Comprehensive family photo session. Includes:
           • 3 hour session
           • Two locations
           • Multiple outfit changes
           • 75-100 edited photos
           • Group, individual, and candid shots
           • Online gallery delivery
           • Personal printing rights
           • Premium photo album
           • Up to 15 people""",
            base_price=Decimal("450.00"),
            duration="3 hr",
            order=3,
        )

        # Family Mini Session
        mini_family = Service.objects.create(
            category=family_cat,
            name="Family Mini Session",
            description="""Quick update of your family photos. Includes:
           • 30 minute session
           • One location
           • One outfit
           • 15-20 edited photos
           • Online gallery delivery
           • Personal printing rights
           • Up to 5 people""",
            base_price=Decimal("150.00"),
            duration="30 min",
            order=4,
        )

        # Add-ons
        family_addons = [
            {
                "name": "Additional Family Members",
                "description": "For groups larger than package limit",
                "price": Decimal("25.00"),
                "unit": "per person",
            },
            {
                "name": "Additional Location",
                "description": "Extra shooting location",
                "price": Decimal("75.00"),
                "unit": "per location",
            },
            {
                "name": "Outfit Change",
                "description": "Additional outfit change opportunity",
                "price": Decimal("25.00"),
                "unit": "per change",
            },
            {
                "name": "Premium Photo Album",
                "description": "20-page professional photo album",
                "price": Decimal("200.00"),
                "unit": "per album",
            },
            {
                "name": "Pet Photography",
                "description": "Include your furry family members",
                "price": Decimal("50.00"),
                "unit": "per session",
            },
            {
                "name": "Extended Session Time",
                "description": "Additional photography time",
                "price": Decimal("100.00"),
                "unit": "per hour",
            },
            {
                "name": "Rush Editing",
                "description": "48-hour delivery",
                "price": Decimal("100.00"),
                "unit": "per session",
            },
            {
                "name": "Print Package",
                "description": "Selection of professional prints",
                "price": Decimal("150.00"),
                "unit": "per package",
            },
        ]

        # Create add-ons for all packages
        for package in [basic_family, extended_family, premium_family, mini_family]:
            for addon in family_addons:
                AddOn.objects.create(service=package, **addon)

        self.stdout.write(
            self.style.SUCCESS("Successfully created family photography packages")
        )
