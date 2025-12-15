from django.db import models
from usuarios.models import Evaluador, Participante
from proyectos.models import Proyecto
from eventos.models import Evento, InstrumentoEvaluacion, ItemInstrumento

class Evaluacion(models.Model):
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    puntaje = models.DecimalField(max_digits=4, decimal_places=2)
    observaciones = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('evaluador', 'proyecto') 

    def __str__(self):
        return f"{self.evaluador.usuario.email} → {self.proyecto.titulo}"

class CalificacionParticipante(models.Model):
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    instrumento = models.ForeignKey(InstrumentoEvaluacion, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemInstrumento, on_delete=models.CASCADE)
    puntaje = models.DecimalField(max_digits=6, decimal_places=2)
    observaciones = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('evaluador', 'participante', 'evento', 'instrumento', 'item')

    def __str__(self):
        return f"{self.participante.usuario.email} - {self.item.nombre} ({self.puntaje})"
