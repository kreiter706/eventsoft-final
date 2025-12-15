from django.db import models
from django.conf import settings
from django.utils import timezone

class EventAdminAccessCode(models.Model):
	ESTADO_CHOICES = [
		('activo', 'Activo'),
		('suspendido', 'Suspendido'),
		('cancelado', 'Cancelado'),
	]
	admin = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_access_code')
	code = models.CharField(max_length=20, unique=True)
	max_events = models.PositiveIntegerField(null=True, blank=True, help_text="Máximo número de eventos permitidos")
	expires_at = models.DateTimeField(null=True, blank=True, help_text="Fecha/hora de expiración del código")
	estado = models.CharField(max_length=12, choices=ESTADO_CHOICES, default='activo')

	def is_valid(self):
		if self.estado != 'activo':
			return False
		if self.expires_at and timezone.now() > self.expires_at:
			return False
		if self.max_events is not None:
			eventos_creados = self.admin.eventos_creados.count()
			if eventos_creados >= self.max_events:
				return False
		return True

	def __str__(self):
		return f"{self.admin.username} - {self.code}"
