from django.db import models
from usuarios.models import Usuario
from inscripciones.models import InscripcionEvento


class DocumentoUsuario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=100)  # ejemplo: "Hoja de vida", "Carta motivación"
    archivo = models.FileField(upload_to='documentos/')
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} de {self.usuario.email}"
class DocumentoParticipante(models.Model):
    inscripcion = models.ForeignKey(InscripcionEvento, on_delete=models.CASCADE, related_name='documentos')
    archivo = models.FileField(upload_to='documentos_participantes/')
    descripcion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Documento de {self.inscripcion.usuario.email} para {self.inscripcion.evento.nombre}"