from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': _("Por favor ingrese un correo y contraseña correctos. Tenga en cuenta que ambos campos pueden ser sensibles a mayúsculas y minúsculas."),
        'inactive': _("Esta cuenta está inactiva."),
    }
