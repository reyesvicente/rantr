# Generated by Django 4.2.5 on 2023-11-13 09:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rants", "0010_alter_rant_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="rant",
            name="views",
            field=models.PositiveIntegerField(default=0),
        ),
    ]