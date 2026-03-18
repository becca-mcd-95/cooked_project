from __future__ import annotations

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0004_recipe_origin_country"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="cuisine",
            field=models.CharField(blank=True, db_index=True, default="", max_length=60),
        ),
        migrations.AddField(
            model_name="recipe",
            name="difficulty",
            field=models.PositiveSmallIntegerField(
                db_index=True,
                default=0,
                help_text="0 = unspecified, 1-5 increasing difficulty.",
                validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)],
            ),
        ),
        migrations.AddField(
            model_name="recipe",
            name="occasion",
            field=models.CharField(blank=True, db_index=True, default="", max_length=60),
        ),
    ]

