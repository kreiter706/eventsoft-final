from django.db import models
from usuarios.models import Participante
from eventos.models import Evento


class Proyecto(models.Model):
    participantes = models.ManyToManyField(Participante, related_name='proyectos')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to='proyectos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        participantes_str = ', '.join([p.usuario.email for p in self.participantes.all()])
        return f"{self.titulo} ({participantes_str})"
