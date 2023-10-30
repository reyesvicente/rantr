# Generated by Django 4.2.5 on 2023-10-30 04:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rants", "0008_rename_uid_rant_uuid_alter_rant_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="rant",
            name="popularity_score",
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
