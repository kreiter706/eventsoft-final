from django.core.management.base import BaseCommand, CommandError
import json


class Command(BaseCommand):
    help = 'Diagnostica problemas de autenticación para un usuario (por email o username)'

    def add_arguments(self, parser):
        parser.add_argument('--username', '-u', type=str, help='Email o username del usuario', required=True)
        parser.add_argument('--password', '-p', type=str, help='(Opcional) contraseña a verificar')

    def handle(self, *args, **options):
        username = options.get('username')
        password = options.get('password')
        # Import aquí para evitar problemas si se usa fuera del contexto de Django
        try:
            from usuarios.models import Usuario
        except Exception as e:
            raise CommandError(f'Error importando Usuario: {e}')

        user = Usuario.objects.filter(email__iexact=username).first() or Usuario.objects.filter(username__iexact=username).first()
        if not user:
            out = {'exists': False}
            self.stdout.write(json.dumps(out, default=str))
            return

        perfiles = {}
        for rel in ('participante', 'evaluador', 'asistente', 'admin_evento'):
            try:
                obj = getattr(user, rel)
                perfiles[rel] = getattr(obj, 'estado', None)
            except Exception:
                perfiles[rel] = None

        # access_code if exists
        ac_info = None
        try:
            ac = getattr(user, 'event_access_code', None)
            if ac:
                ac_info = {
                    'estado': getattr(ac, 'estado', None),
                    'expires_at': getattr(ac, 'expires_at', None),
                }
        except Exception:
            ac_info = None

        result = {
            'exists': True,
            'email': user.email,
            'username': user.username,
            'is_active': user.is_active,
            'has_usable_password': user.has_usable_password(),
            'check_password': user.check_password(password) if password else None,
            'rol': user.rol,
            'perfiles': perfiles,
            'access_code': ac_info,
        }

        self.stdout.write(json.dumps(result, default=str))
