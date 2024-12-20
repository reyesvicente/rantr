# Generated by Django 5.1.2 on 2024-11-25 08:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0003_alter_comment_rant"),
        ("rants", "0013_alter_rant_options_alter_rant_image_alter_rant_likes_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={"ordering": ["-created"]},
        ),
        migrations.AddField(
            model_name="comment",
            name="likes",
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name="comment",
            name="content",
            field=models.TextField(max_length=500),
        ),
        migrations.AlterField(
            model_name="comment",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="replies",
                to="comments.comment",
            ),
        ),
        migrations.AlterField(
            model_name="comment",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="comments", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["rant", "-created"], name="comments_co_rant_id_7f8c86_idx"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["user", "-created"], name="comments_co_user_id_18a5c7_idx"),
        ),
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["parent", "-created"], name="comments_co_parent__952a7a_idx"),
        ),
    ]
