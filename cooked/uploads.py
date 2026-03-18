import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/gif", "image/webp"}


def save_recipe_photo(upload: UploadedFile) -> str:
    name = upload.name or ""
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("Unsupported image type.")
    if getattr(upload, "content_type", None) and upload.content_type not in ALLOWED_IMAGE_MIMES:
        raise ValueError("Unsupported image type.")

    root = Path(getattr(settings, "RECIPE_UPLOAD_ROOT", str(Path(settings.BASE_DIR) / "static/uploads/recipes")))
    root.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = root / filename

    with abs_path.open("wb") as f:
        for chunk in upload.chunks():
            f.write(chunk)

    static_root = Path(settings.BASE_DIR) / "static"
    rel = abs_path.relative_to(static_root)
    return rel.as_posix()


def delete_recipe_photo(static_rel_path: str) -> None:
    if not static_rel_path:
        return

    static_root = (Path(settings.BASE_DIR) / "static").resolve()
    abs_path = (static_root / static_rel_path).resolve()
    uploads_root = (static_root / "uploads" / "recipes").resolve()

    if uploads_root not in abs_path.parents:
        return
    if abs_path.exists() and abs_path.is_file():
        try:
            os.remove(abs_path)
        except OSError:
            return
