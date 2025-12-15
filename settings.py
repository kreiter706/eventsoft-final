
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    # Otras aplicaciones...
    'usuarios.apps.UsuariosConfig',
    'eventos',
    'evaluaciones',
    # ...
]



STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / "static/css_generales",
]
# Configuración de email para Django (agrega esto en tu settings.py)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # Para pruebas, muestra los correos en la terminal
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'gworshop26@gmail.com'  # Cambia por tu correo
EMAIL_HOST_PASSWORD = 'ydso hsiz kvnj zfun'  # Cambia por tu contraseña o app password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
LOGOUT_REDIRECT_URL = '/usuarios/login/'

