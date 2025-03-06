# Generated by Django 5.0.1 on 2025-02-24 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photo_app", "0003_cherryblossomsession"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cherryblossomsession",
            name="duration",
            field=models.IntegerField(default=30),
        ),
        migrations.AlterField(
            model_name="contact",
            name="service",
            field=models.CharField(
                choices=[
                    ("Portrait/Headshot", "Portrait/Headshot"),
                    ("Studio Portrait/Headshot", "Studio Portrait/Headshot"),
                    ("Wedding", "Wedding"),
                    ("Event", "Event"),
                    ("Family", "Family"),
                    ("Graduation", "Graduation"),
                    ("Engagement", "Engagement"),
                    ("Couples", "Couples"),
                    ("Corporate", "Corporate"),
                    ("Second Shooter", "Second Shooter"),
                    ("Wedding Videography", "Wedding Videography"),
                    ("Event Videography", "Event Videography"),
                    ("Other Services", "Other Services"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
