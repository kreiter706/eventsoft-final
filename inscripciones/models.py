from django.db import models
from usuarios.models import Usuario
from eventos.models import Evento

class InscripcionEvento(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('admitido', 'Admitido'),
        ('no_admitido', 'No admitido'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    clave_acceso = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        unique_together = ('usuario', 'evento')

    def __str__(self):
        return f"{self.usuario.email} en {self.evento.nombre}"