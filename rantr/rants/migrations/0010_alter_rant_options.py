# Generated by Django 4.2.5 on 2023-10-30 04:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rants", "0009_rant_popularity_score"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="rant",
            options={"verbose_name": "rant", "verbose_name_plural": "rants"},
        ),
    ]
