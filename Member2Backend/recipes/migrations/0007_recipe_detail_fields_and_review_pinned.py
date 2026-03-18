from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0006_recipe_difficulty_nullable"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="description",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="recipe",
            name="prep_time_minutes",
            field=models.PositiveSmallIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name="recipe",
            name="serving_size",
            field=models.CharField(blank=True, default="", max_length=60),
        ),
        migrations.AddField(
            model_name="review",
            name="pinned",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]

