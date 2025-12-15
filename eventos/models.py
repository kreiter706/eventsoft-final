
from django.db import models
from usuarios.models import Evaluador

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Evento(models.Model):
    nombre = models.CharField(max_length=255)
    creador = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos_creados', help_text='Administrador que creó el evento')
    categoria = models.ForeignKey('Categoria', on_delete=models.SET_NULL, null=True, blank=True, related_name='eventos')
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    lugar = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    cupos = models.PositiveIntegerField(null=True, blank=True)
    requiere_evaluacion = models.BooleanField(default=False)
    costo_inscripcion = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inscripciones_habilitadas = models.BooleanField(default=True)  
    inscripciones_participante = models.BooleanField("Inscripciones habilitadas para participantes", default=True)
    inscripciones_evaluador = models.BooleanField("Inscripciones habilitadas para evaluadores", default=True)
    inscripciones_asistente = models.BooleanField("Inscripciones habilitadas para asistentes", default=True)
    imagen = models.ImageField(upload_to='imagenes_eventos/', blank=True, null=True)
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return self.nombre

class PresentacionEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='presentaciones')
    archivo = models.FileField(upload_to='presentaciones_evento/')
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.evento.nombre})"

class ConfiguracionCertificadoEvento(models.Model):
    evento = models.OneToOneField(Evento, on_delete=models.CASCADE, related_name='configuracion_certificado')
    nombre_evento = models.CharField(max_length=255, blank=True)
    fecha_inicio_evento = models.DateField(null=True, blank=True)
    fecha_fin_evento = models.DateField(null=True, blank=True)
    lugar_evento = models.CharField(max_length=255, blank=True)
    organizador_evento = models.CharField(max_length=255, blank=True)
    mensaje_certificado = models.TextField(blank=True)

    def __str__(self):
        return f"Configuración certificado de {self.evento.nombre}"


class ProgramacionEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='programaciones')
    titulo_actividad = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    lugar = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.titulo_actividad} ({self.evento.nombre})"

class Asistente(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  
    def __str__(self):
        return self.nombre

class InstrumentoEvaluacion(models.Model):
    TIPOS = [
        ('rubrica', 'Rúbrica'),
        ('chequeo', 'Lista de Chequeo'),
        ('plantilla', 'Plantilla'),
    ]
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='instrumentos')
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='instrumentos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

from django.core.exceptions import ValidationError

# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\models.py
# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\models.py
class ItemInstrumento(models.Model):
    instrumento = models.ForeignKey(InstrumentoEvaluacion, on_delete=models.CASCADE, related_name='items')
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    puntaje_maximo = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    peso_porcentaje = models.DecimalField("Peso (%)", max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return self.nombre

    def clean(self):
        # Validación para que el total del peso porcentaje no supere el 100%
        if not self.instrumento_id:  # Si el instrumento no está asignado, no validar
            return

        total_peso = sum(item.peso_porcentaje for item in ItemInstrumento.objects.filter(instrumento_id=self.instrumento_id).exclude(pk=self.pk))
        total_peso += self.peso_porcentaje

        if total_peso > 100:
            raise ValidationError(f"El total del peso porcentaje no puede superar el 100%. Actualmente: {total_peso}%.")

    def save(self, *args, **kwargs):
        self.clean()  # Llama a la validación antes de guardar
        super().save(*args, **kwargs)

class EvaluadorEvento(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('admitido', 'Admitido'),
        ('rechazado', 'Rechazado'),
    ]
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE, related_name='eventos_asignados')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='evaluadores_asignados')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    class Meta:
        unique_together = ('evaluador', 'evento')

    def __str__(self):
        return f"{self.evaluador.usuario.email} en {self.evento.nombre} ({self.get_estado_display()})"

class InfoTecnicaEvento(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='info_tecnica')
    evaluador = models.ForeignKey(Evaluador, on_delete=models.CASCADE)
    descripcion = models.TextField("Descripción técnica", blank=True)
    archivo = models.FileField(upload_to='info_tecnica_evento/', blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Info técnica de {self.evento.nombre} por {self.evaluador.usuario.email}"