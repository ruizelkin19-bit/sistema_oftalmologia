import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Cargar variables de entorno desde .env
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "clave-secreta-en-caso-de-fallo")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

# Aplicaciones instaladas
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps del proyecto
    'core',
    'pacientes',
    'citas',
    'inventario',
    'historias',
    'productos',
    'rips',
    'widget_tweaks',
    'pacientes.templatetags.form_filters',
    'informes',
    'django_extensions',
    'facturacion',
    'tarifas',
    'admisiones',
    'soportes',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Para servir static en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.ips_config',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Base de datos (Render)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL")
    )
}

# Validadores de contraseña
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Idioma y zona horaria
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Archivos estáticos para Render
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"  # Aquí se copia todo con collectstatic
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Login
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/admin/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Jazzmin
JAZZMIN_SETTINGS = {
    "site_title": "Sistema Oftalmológico",
    "site_header": "Panel de Administración",
    "site_brand": "Oftalmología",
    "site_logo": "img/logo.png",
    "welcome_sign": "Bienvenida Leydis Jiménez",
    "copyright": "© 2025",
    "topmenu_links": [
        {"name": "Inicio", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"app": "pacientes"},
        {"app": "citas"},
        {"app": "inventario"},
        {"model": "auth.user"},
    ],
    "icons": {
        "auth.user": "fas fa-user-shield",
        "auth.Group": "fas fa-users-cog",
        "pacientes.Paciente": "fas fa-user-injured",
        "citas.Cita": "fas fa-calendar-check",
        "inventario.Producto": "fas fa-boxes",
        "productos.Producto": "fas fa-box-open",
        "historias.HistoriaClinica": "fas fa-notes-medical",
        "rips.RipArchivo": "fas fa-file-medical",
    },
    "order_with_respect_to": ["pacientes", "citas", "inventario", "historias", "rips"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "custom_links": {},
}

# Datos IPS
IPS_CONFIG = {
    "nombre": "GABRIEL ANTONIO CHILD ESCOBAR",
    "nit": "3.228.541-4",
    "direccion": "Calle 93 No. 15-51 Of. 206, Bogotá",
    "telefono": "(601) 6185299",
    "email": "contacto@ipsxyz.com",
}

# Permitir PDFs en iframe
X_FRAME_OPTIONS = 'SAMEORIGIN'
