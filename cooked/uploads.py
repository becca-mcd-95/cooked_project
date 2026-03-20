import os
import uuid
from pathlib import Path
import cloudinary
import cloudinary.uploader

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile


# Yanyan

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/gif", "image/webp"}


def save_recipe_photo(upload: UploadedFile) -> str:
    name = upload.name or ""
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("Unsupported image type.")
    if getattr(upload, "content_type", None) and upload.content_type not in ALLOWED_IMAGE_MIMES:
        raise ValueError("Unsupported image type.")

    result = cloudinary.uploader.upload(
        upload,
        folder="recipes",
        resource_type="image"
    )
    return result["secure_url"]

# trying to use cloudinary for image as the way this was set up wasn't working commenting out for now

def delete_recipe_photo(static_rel_path: str) -> None:
    pass

# def delete_recipe_photo(static_rel_path: str) -> None:
#     if not static_rel_path:
#         return

#     static_root = (Path(settings.BASE_DIR) / "static").resolve()
#     abs_path = (static_root / static_rel_path).resolve()
#     uploads_root = (static_root / "uploads" / "recipes").resolve()

#     if uploads_root not in abs_path.parents:
#         return
#     if abs_path.exists() and abs_path.is_file():
#         try:
#             os.remove(abs_path)
#         except OSError:
#             return
        
# Tuoyu

def _save_image(upload: UploadedFile, root_setting: str, default_rel_dir: str) -> str:
    name = upload.name or ""
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise ValueError("Unsupported image type.")
    if getattr(upload, "content_type", None) and upload.content_type not in ALLOWED_IMAGE_MIMES:
        raise ValueError("Unsupported image type.")

    root = Path(getattr(settings, root_setting, str(Path(settings.BASE_DIR) / "static" / default_rel_dir)))
    root.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = root / filename
    with abs_path.open("wb") as f:
        for chunk in upload.chunks():
            f.write(chunk)

    static_root = Path(settings.BASE_DIR) / "static"
    rel = abs_path.relative_to(static_root)
    return rel.as_posix()


def _delete_image(static_rel_path: str, uploads_subdir: str) -> None:
    if not static_rel_path:
        return

    static_root = (Path(settings.BASE_DIR) / "static").resolve()
    abs_path = (static_root / static_rel_path).resolve()
    uploads_root = (static_root / "uploads" / uploads_subdir).resolve()

    if uploads_root not in abs_path.parents:
        return
    if abs_path.exists() and abs_path.is_file():
        try:
            os.remove(abs_path)
        except OSError:
            return


def save_avatar(upload: UploadedFile) -> str:
    return _save_image(upload, "PROFILE_AVATAR_UPLOAD_ROOT", "uploads/avatars")


def save_cover(upload: UploadedFile) -> str:
    return _save_image(upload, "PROFILE_COVER_UPLOAD_ROOT", "uploads/covers")


def delete_avatar(static_rel_path: str) -> None:
    _delete_image(static_rel_path, "avatars")


def delete_cover(static_rel_path: str) -> None:
    _delete_image(static_rel_path, "covers")