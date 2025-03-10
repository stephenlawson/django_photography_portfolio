# Generated by Django 5.0.1 on 2025-02-24 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photo_app", "0002_alter_video_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="CherryBlossomSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("is_booked", models.BooleanField(default=False)),
                (
                    "location",
                    models.CharField(
                        default="Windsor Way & Cary St, Richmond VA 23221",
                        max_length=200,
                    ),
                ),
                ("duration", models.IntegerField(default=15)),
                (
                    "price",
                    models.DecimalField(decimal_places=2, default=175.0, max_digits=6),
                ),
                (
                    "client_name",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
                (
                    "client_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
            ],
            options={
                "ordering": ["date", "start_time"],
            },
        ),
    ]
