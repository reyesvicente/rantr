# Generated by Django 4.2.9 on 2024-10-30 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rants", "0011_rant_views"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rant",
            name="popularity_score",
            field=models.DecimalField(decimal_places=5, default=0.0, max_digits=10),
        ),
    ]