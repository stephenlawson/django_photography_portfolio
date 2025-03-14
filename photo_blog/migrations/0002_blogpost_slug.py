# Generated by Django 4.1.2 on 2023-11-28 21:15

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("photo_blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="slug",
            field=autoslug.fields.AutoSlugField(
                default="test", editable=False, populate_from="title", unique=True
            ),
            preserve_default=False,
        ),
    ]
