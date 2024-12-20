# Generated by Django 5.1.2 on 2024-11-25 08:15

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("verb", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("target_object_id", models.PositiveIntegerField(blank=True, null=True)),
                ("unread", models.BooleanField(db_index=True, default=True)),
                ("timestamp", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("deleted", models.BooleanField(default=False)),
                (
                    "actor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="actions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "target_content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications_target",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
                "indexes": [
                    models.Index(fields=["recipient", "unread"], name="notificatio_recipie_8bedf2_idx"),
                    models.Index(fields=["recipient", "timestamp"], name="notificatio_recipie_236852_idx"),
                ],
            },
        ),
    ]
