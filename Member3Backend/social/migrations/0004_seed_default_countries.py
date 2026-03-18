from __future__ import annotations

from django.db import migrations


DEFAULT_COUNTRIES: tuple[tuple[str, str], ...] = (
    ("CN", "China"),
    ("FR", "France"),
    ("IT", "Italy"),
    ("JP", "Japan"),
    ("GB", "United Kingdom"),
    ("US", "United States"),
    ("ES", "Spain"),
    ("MX", "Mexico"),
    ("IN", "India"),
    ("TH", "Thailand"),
    ("KR", "South Korea"),
    ("TR", "Turkey"),
)


def has_cjk(text: str) -> bool:
    for ch in text:
        code = ord(ch)
        if (
            0x4E00 <= code <= 0x9FFF
            or 0x3400 <= code <= 0x4DBF
            or 0x3040 <= code <= 0x30FF
            or 0xAC00 <= code <= 0xD7AF
        ):
            return True
    return False


def seed_default_countries(apps, schema_editor) -> None:
    Country = apps.get_model("social", "Country")

    for iso2, name in DEFAULT_COUNTRIES:
        obj, created = Country.objects.get_or_create(iso2=iso2, defaults={"name": name})
        if created:
            continue
        if (not obj.name) or has_cjk(obj.name):
            obj.name = name
            obj.save(update_fields=["name"])


class Migration(migrations.Migration):
    dependencies = [
        ("social", "0003_profile"),
    ]

    operations = [
        migrations.RunPython(seed_default_countries, migrations.RunPython.noop),
    ]
