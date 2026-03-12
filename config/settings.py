from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Allow Django apps to live under Member2/Member3 backend folders while keeping
# their import paths as `recipes` and `social`.
for backend_dir in (BASE_DIR / "Member2Backend", BASE_DIR / "Member3Backend"):
    backend_dir_str = str(backend_dir)
    if backend_dir.exists() and backend_dir_str not in sys.path:
        sys.path.insert(0, backend_dir_str)

# Load environment variables from the project root, regardless of current working directory.
# Prefer `.env` (user-specific), fallback to `.env.django.example` (sane defaults for this repo).
if not load_dotenv(BASE_DIR / ".env"):
    load_dotenv(BASE_DIR / ".env.django.example")


def env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-secret-key-change-me")
DEBUG = env_bool("DJANGO_DEBUG", True)


def _parse_allowed_hosts(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        return []

    hosts: list[str] = []
    wildcard = False
    for item in raw.split(","):
        h = item.strip()
        if not h:
            continue

        if h.startswith("http://") or h.startswith("https://"):
            h = h.split("://", 1)[1]
        h = h.split("/", 1)[0]

        # Strip "host:port" for common cases. (Do not try to parse IPv6 here.)
        if ":" in h and h.count(":") == 1 and not h.startswith("["):
            h = h.split(":", 1)[0]

        # NOTE: "0.0.0.0" is commonly used for binding, not for Host headers.
        if h in {"*", "0.0.0.0"}:
            wildcard = True
        else:
            hosts.append(h)

    return ["*"] if wildcard else hosts


allowed_hosts = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost")
ALLOWED_HOSTS = _parse_allowed_hosts(allowed_hosts)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "recipes",
    "social",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            str(BASE_DIR / "Member2Frontend"),
            str(BASE_DIR / "Member3Frontend"),
            str(BASE_DIR / "django_templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social.context_processors.notification_count",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"


def _database_from_url(url: str):
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme in {"mysql", "mysql+connector", "mysql+mysqlclient"}:
        query = parse_qs(parts.query or "")
        name = parts.path.lstrip("/") or "recipeboxd_django"
        options = {}
        charset = (query.get("charset") or ["utf8mb4"])[0]
        options["charset"] = charset
        engine = os.environ.get("DJANGO_MYSQL_ENGINE", "mysql.connector.django").strip() or "mysql.connector.django"
        if scheme == "mysql+mysqlclient":
            engine = "django.db.backends.mysql"
        if engine == "mysql.connector.django":
            try:
                import mysql.connector  # noqa: F401
            except Exception as e:
                raise RuntimeError(
                    "MySQL is configured but mysql-connector-python is not installed. "
                    "Run: python -m pip install mysql-connector-python"
                ) from e
        return {
            "ENGINE": engine,
            "NAME": name,
            "USER": parts.username or "root",
            "PASSWORD": parts.password or "",
            "HOST": parts.hostname or "127.0.0.1",
            "PORT": str(parts.port or 3306),
            "OPTIONS": options,
        }
    if scheme.startswith("sqlite"):
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": str(BASE_DIR / "db.sqlite3")}
    raise ValueError(f"Unsupported DATABASE_URL scheme: {scheme}")


DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
if DATABASE_URL:
    DATABASES = {"default": _database_from_url(DATABASE_URL)}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": str(BASE_DIR / "db.sqlite3")}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [str(BASE_DIR / "static")]
STATIC_ROOT = str(BASE_DIR / "staticfiles")

RECIPE_UPLOAD_ROOT = str(BASE_DIR / "static" / "uploads" / "recipes")

MEDIA_URL = "media/"
MEDIA_ROOT = str(BASE_DIR / "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "recipe_list"
LOGOUT_REDIRECT_URL = "recipe_list"
