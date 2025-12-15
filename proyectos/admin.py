
from django.contrib import admin
from .models import Proyecto
from usuarios.models import Participante
from .utils import enviar_correo_admision_participante

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
	list_display = ("titulo", "evento")
	actions = ["enviar_correos_admision"]

	def enviar_correos_admision(self, request, queryset):
		for proyecto in queryset:
			participantes = proyecto.participantes.all()
			representante = participantes.first() if participantes else None
			for participante in participantes:
				enviar_correo_admision_participante(participante, proyecto.evento, representante=representante)
		self.message_user(request, "Correos de admisión enviados a todos los participantes del proyecto.")
	enviar_correos_admision.short_description = "Enviar correo de admisión a todos los participantes"
