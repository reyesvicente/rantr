# Generated by Django 4.2.5 on 2023-10-20 12:28

import autoslug.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("rants", "0006_alter_rant_options"),
    ]

    operations = [
        migrations.RenameField(
            model_name="rant",
            old_name="uuid",
            new_name="uid",
        ),
        migrations.AlterField(
            model_name="rant",
            name="slug",
            field=autoslug.fields.AutoSlugField(editable=False, populate_from="uid"),
        ),
    ]