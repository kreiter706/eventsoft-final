from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Permite autenticación usando email en el campo username
        if username is None:
            username = kwargs.get('email')
        if username:
            username = username.strip()
        # Try exact email match first
        user = None
        if username:
            try:
                user = Usuario.objects.get(email__iexact=username)
            except Usuario.DoesNotExist:
                try:
                    user = Usuario.objects.get(username__iexact=username)
                except Usuario.DoesNotExist:
                    user = None
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None