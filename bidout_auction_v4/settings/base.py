from pathlib import Path
from decouple import config
import os
import logging
import logging.config

from django.utils.log import DEFAULT_LOGGING

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG")

ALLOWED_HOSTS = config("ALLOWED_HOSTS").split(" ")

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.common.exceptions.custom_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.AllowAny",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Application definition

DJANGO_APPS = [
    "django.contrib.contenttypes",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

SITE_ID = 1

THIRD_PARTY_APPS = [
    "adrf",
    "corsheaders",
    "cloudinary",
    "debug_toolbar",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.common",
    "apps.accounts",
    "apps.general",
    "apps.listings",
    "apps.auctioneer",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

CORS_ALLOW_HEADERS = (
    "x-requested-with",
    "content-type",
    "accept",
    "origin",
    "authorization",
    "accept-encoding",
    "access-control-allow-origin",
    "content-disposition",
)

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS").split(" ")
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")

SPECTACULAR_SETTINGS = {
    "TITLE": "BIDOUT AUCTION API",
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
            "guestUserID": {
                "type": "apiKey",
                "in": "header",
                "name": "guestUserID",
                "description": "For guest watchlists. Get ID from '/api/v4/listings/watchlist' POST endpoint",
            },
        }
    },
    "SECURITY": [
        {
            "bearerAuth": [],
            "guestUserID": [],
        }
    ],
    "DESCRIPTION": "A Simple Bidding API built with Django Rest Framework",
    "VERSION": "4.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "AUTHENTICATION_WHITELIST": [],
}

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bidout_auction_v4.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bidout_auction_v4.wsgi.application"


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Lagos"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/"),
]

MEDIA_ROOT = os.path.join(BASE_DIR, "static/media")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email Settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_SSL = config("EMAIL_USE_SSL")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL")

INTERNAL_IPS = [
    "127.0.0.1",
]
SITE_NAME = config("SITE_NAME")
FRONTEND_URL = config("FRONTEND_URL")

logger = logging.getLogger(__name__)

LOG_LEVEL = "INFO"

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
            "file": {"format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"},
            "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "file",
                "filename": "logs/bidout_auction_v4.log",
            },
            "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
        },
        "loggers": {
            "": {
                "level": "INFO",
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "apps": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        },
    }
)

JAZZMIN_SETTINGS = {
    # title of the window (Will default to current_admin_site.site_title if absent or None)
    "site_title": "BIDOUT AUCTION V4 ADMIN",
    # Title on the login screen (19 chars max) (defaults to current_admin_site.site_header if absent or None)
    "site_header": "B.A V4",
    # Logo to use for your site, must be present in static files, used for brand on top left
    "site_logo": "media/banner2-icon3.png",
    # CSS classes that are applied to the logo above
    "site_logo_classes": "img-circle",
    # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
    "login_logo": "media/banner2-icon3.png",
    # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
    "site_icon": "media/logo.png",
    # Welcome text on the login screen
    "welcome_sign": "Welcome to the Bidout Auction v4 Admin Section",
    # Copyright on the footer
    "copyright": "Bidout Auction v4 Ltd",
    # The model admin to search from the search bar, search bar omitted if excluded
    "search_model": "accounts.User",
    # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
    "user_avatar": "avatar",
    ############
    # Top Menu #
    ############
    # Links to put along the top menu
    "topmenu_links": [
        # Url that gets reversed (Permissions can be added)
        {
            "name": "Home",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },
        # model admin to link to (Permissions checked against model)
        # {"model": "accounts.User"},
        # App with dropdown menu to all its models pages (Permissions checked against models)
        {"app": "accounts"},
        {"app": "general"},
        {"app": "listings"},
    ],
    #############
    # User Menu #
    #############
    # Additional links to include in the user menu on the top right ("app" url type is not allowed)
    "usermenu_links": [
        {"name": "BA V4 FrontPage", "url": FRONTEND_URL, "new_window": True},
        {"model": "accounts.user"},
    ],
    #############
    # Side Menu #
    #############
    # Whether to display the side menu
    "show_sidebar": True,
    # Whether to aut expand the menu
    "navigation_expanded": True,
    # Hide these apps when generating side menu e.g (auth)
    "hide_apps": [],
    # Hide these models when generating side menu (e.g auth.user)
    "hide_models": [],
    # List of apps (and/or models) to base side menu ordering off of (does not need to contain all apps/models)
    # "order_with_respect_to": ["auth", "accounts", "accounts.user", "accounts.tutor", "accounts.student", "lessons"],
    # Custom icons for side menu apps/models See https://fontawesome.com/icons?d=gallery&m=free&v=5.0.0,5.0.1,5.0.10,5.0.11,5.0.12,5.0.13,5.0.2,5.0.3,5.0.4,5.0.5,5.0.6,5.0.7,5.0.8,5.0.9,5.1.0,5.1.1,5.2.0,5.3.0,5.3.1,5.4.0,5.4.1,5.4.2,5.13.0,5.12.0,5.11.2,5.11.1,5.10.0,5.9.0,5.8.2,5.8.1,5.7.2,5.7.1,5.7.0,5.6.3,5.5.0,5.4.2
    # for the full list of 5.13.0 free icon classes
    "icons": {
        "accounts.Group": "fas fa-users",
        "accounts.user": "fas fa-user-cog",
        "common.file": "fas fa-image",
        "common.guestuser": "fas fa-users",
        "general.sitedetail": "fas fa-info-circle",
        "general.subscriber": "fas fa-users",
        "general.review": "fas fa-comments",
        "listings.category": "fas fa-list",
        "listings.listing": "fas fa-list-alt",
        "listings.bid": "fas fa-dollar-sign",
        "listings.watchlist": "fas fa-heart",
        "sites.site": "fas fa-globe",
    },
    # Icons that are used when one is not manually specified
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    #############
    # UI Tweaks #
    #############
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    # override change forms on a per modeladmin basis
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "auth.group": "vertical_tabs",
    },
    # "related_modal_active": True # Won't work in some browsers
}

EMAIL_OTP_EXPIRE_SECONDS = config("EMAIL_OTP_EXPIRE_SECONDS")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES = config("REFRESH_TOKEN_EXPIRE_MINUTES")
FIRST_SUPERUSER_EMAIL = config("FIRST_SUPERUSER_EMAIL")
FIRST_SUPERUSER_PASSWORD = config("FIRST_SUPERUSER_PASSWORD")
FIRST_AUCTIONEER_EMAIL = config("FIRST_AUCTIONEER_EMAIL")
FIRST_AUCTIONEER_PASSWORD = config("FIRST_AUCTIONEER_PASSWORD")
FIRST_REVIEWER_EMAIL = config("FIRST_REVIEWER_EMAIL")
FIRST_REVIEWER_PASSWORD = config("FIRST_REVIEWER_PASSWORD")
CLOUDINARY_CLOUD_NAME = config("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = config("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = config("CLOUDINARY_API_SECRET")
