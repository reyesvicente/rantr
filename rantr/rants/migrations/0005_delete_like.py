# Generated by Django 4.2.5 on 2023-09-30 03:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rants", "0004_rant_image"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Like",
        ),
    ]
