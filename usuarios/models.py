from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    email = models.EmailField(unique=True)

    ROLES = [
        ('participante', 'Participante'),
        ('evaluador', 'Evaluador'),
        ('asistente', 'Asistente'),
        ('admin', 'Administrador de Evento'),      # Cambiado
        ('superadmin', 'Super Administrador'),     # Cambiado
    ]
    rol = models.CharField(max_length=20, choices=ROLES, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Participante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='participante')
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('admitido', 'Admitido'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )
    clave_temporal = models.CharField(max_length=128, blank=True, null=True, help_text="Clave de acceso generada para el envío por correo al ser admitido.")

    def __str__(self):
        return f"{self.usuario.email}"

class Evaluador(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='evaluador')
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('admitido', 'Admitido'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )

    def __str__(self):
        return f"{self.usuario.email}"

class AdministradorEvento(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='admin_evento')
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('admitido', 'Admitido'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )

    def __str__(self):
        return f"{self.usuario.email}"

class Asistente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='asistente')
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('admitido', 'Admitido'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )

    def __str__(self):
        return f"{self.usuario.email}"
    
