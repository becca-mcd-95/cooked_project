from __future__ import annotations

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0005_recipe_browse_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="difficulty",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                db_index=True,
                default=None,
                help_text="1-5 increasing difficulty (leave blank if unspecified).",
                validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)],
            ),
        ),
    ]

