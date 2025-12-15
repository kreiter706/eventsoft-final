from django.contrib import admin
from .models import Categoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
from django.contrib import admin
from .models import Evento, ProgramacionEvento, InstrumentoEvaluacion, ItemInstrumento

admin.site.register(Evento)
admin.site.register(ProgramacionEvento)
admin.site.register(InstrumentoEvaluacion)
admin.site.register(ItemInstrumento)

from .models import EvaluadorEvento

@admin.register(EvaluadorEvento)
class EvaluadorEventoAdmin(admin.ModelAdmin):
    list_display = ('evaluador', 'evento', 'estado')
    list_filter = ('estado', 'evento')
    search_fields = ('evaluador__usuario__email', 'evento__nombre')

from .utils import notificar_asistentes_evento
from django import forms
from django.contrib import messages

class NotificarAsistentesForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    asunto = forms.CharField(label="Asunto", max_length=200)
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea)

def notificar_asistentes(modeladmin, request, queryset):
    if 'apply' in request.POST:
        form = NotificarAsistentesForm(request.POST)
        if form.is_valid():
            asunto = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']
            for evento in queryset:
                notificar_asistentes_evento(evento, asunto, mensaje)
            modeladmin.message_user(request, "Notificaciones enviadas a los asistentes.", messages.SUCCESS)
            return
    else:
        form = NotificarAsistentesForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    return admin.helpers.render_action_form(
        request,
        form,
        'Enviar notificación a asistentes',
        '¿Estás seguro de que deseas enviar esta notificación a los asistentes de los eventos seleccionados?'
    )
notificar_asistentes.short_description = "Notificar a asistentes por email"

from inscripciones.models import InscripcionEvento
from .certificados import enviar_certificado_asistencia

def enviar_certificados(modeladmin, request, queryset):
    enviados = 0
    for evento in queryset:
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente', estado='admitido')
        for inscripcion in inscripciones:
            asistente = getattr(inscripcion.usuario, 'asistente', None)
            if asistente:
                enviar_certificado_asistencia(asistente, evento)
                enviados += 1
    modeladmin.message_user(request, f"Certificados enviados: {enviados}", messages.SUCCESS)
enviar_certificados.short_description = "Enviar certificados de asistencia a asistentes"

from .certificados_participante import enviar_certificado_participacion

def enviar_certificados_participacion(modeladmin, request, queryset):
    enviados = 0
    for evento in queryset:
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='participante', estado='admitido')
        for inscripcion in inscripciones:
            participante = getattr(inscripcion.usuario, 'participante', None)
            if participante:
                enviar_certificado_participacion(participante, evento)
                enviados += 1
    modeladmin.message_user(request, f"Certificados de participación enviados: {enviados}", messages.SUCCESS)
enviar_certificados_participacion.short_description = "Enviar certificados de participación a participantes"

from .certificados_evaluador import enviar_certificado_evaluador

def enviar_certificados_evaluador(modeladmin, request, queryset):
    enviados = 0
    from inscripciones.models import InscripcionEvento
    for evento in queryset:
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='evaluador', estado='admitido')
        for inscripcion in inscripciones:
            evaluador = getattr(inscripcion.usuario, 'evaluador', None)
            if evaluador:
                enviar_certificado_evaluador(evaluador, evento)
                enviados += 1
    modeladmin.message_user(request, f"Certificados de evaluador enviados: {enviados}", messages.SUCCESS)
enviar_certificados_evaluador.short_description = "Enviar certificados de evaluación a evaluadores"

from django import forms
from django.contrib import messages
from inscripciones.models import InscripcionEvento

def notificar_evaluadores_evento(evento, asunto, mensaje):
    inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='evaluador', estado='admitido')
    destinatarios = [i.usuario.email for i in inscripciones]
    if destinatarios:
        from django.core.mail import send_mail
        from django.conf import settings
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
        )

class NotificarEvaluadoresForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    asunto = forms.CharField(label="Asunto", max_length=200)
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea)

def notificar_evaluadores(modeladmin, request, queryset):
    if 'apply' in request.POST:
        form = NotificarEvaluadoresForm(request.POST)
        if form.is_valid():
            asunto = form.cleaned_data['asunto']
            mensaje = form.cleaned_data['mensaje']
            for evento in queryset:
                notificar_evaluadores_evento(evento, asunto, mensaje)
            modeladmin.message_user(request, "Notificaciones enviadas a los evaluadores.", messages.SUCCESS)
            return
    else:
        form = NotificarEvaluadoresForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    return admin.helpers.render_action_form(
        request,
        form,
        'Enviar notificación a evaluadores',
        '¿Estás seguro de que deseas enviar esta notificación a los evaluadores de los eventos seleccionados?'
    )
notificar_evaluadores.short_description = "Notificar a evaluadores por email"


from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.shortcuts import get_object_or_404
from inscripciones.models import InscripcionEvento

class EventoAdmin(admin.ModelAdmin):
    actions = [notificar_asistentes, enviar_certificados, enviar_certificados_participacion, enviar_certificados_evaluador, notificar_evaluadores]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:evento_id>/estadisticas/', self.admin_site.admin_view(self.estadisticas_evento), name='evento-estadisticas'),
        ]
        return custom_urls + urls

    def estadisticas_evento(self, request, evento_id):
        evento = get_object_or_404(Evento, id=evento_id)
        inscripciones = InscripcionEvento.objects.filter(evento_id=evento.id)
        total = inscripciones.count()
        participantes = inscripciones.filter(usuario__rol='participante')
        asistentes = inscripciones.filter(usuario__rol='asistente')
        evaluadores = inscripciones.filter(usuario__rol='evaluador')
        data = {
            'evento': evento,
            'total_inscritos': total,
            'participantes_total': participantes.count(),
            'participantes_admitidos': participantes.filter(estado='admitido').count(),
            'asistentes_total': asistentes.count(),
            'asistentes_admitidos': asistentes.filter(estado='admitido').count(),
            'evaluadores_total': evaluadores.count(),
            'evaluadores_admitidos': evaluadores.filter(estado='admitido').count(),
            'cupos': evento.cupos,
            'fecha_inicio': evento.fecha_inicio,
            'fecha_fin': evento.fecha_fin,
            'lugar': evento.lugar,
        }
        return TemplateResponse(request, 'admin/eventos/estadisticas_evento.html', data)

    def estadisticas_link(self, obj):
        return format_html('<a class="button" href="{}">Ver estadísticas</a>',
            reverse('admin:evento-estadisticas', args=[obj.id]))
    estadisticas_link.short_description = 'Estadísticas'
    estadisticas_link.allow_tags = True

    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'lugar', 'cupos', 'estadisticas_link')
    list_editable = ('fecha_inicio', 'fecha_fin', 'hora_inicio', 'hora_fin', 'lugar', 'cupos')

    # Ensure admin form shows the time fields and groups them with the dates
    fieldsets = (
        (None, {
            'fields': ('nombre', 'categoria', 'descripcion', 'imagen')
        }),
        ('Fechas y horarios', {
            'fields': ('fecha_inicio', 'hora_inicio', 'fecha_fin', 'hora_fin')
        }),
        ('Lugar y capacidad', {
            'fields': ('lugar', 'ciudad', 'cupos')
        }),
    )

admin.site.unregister(Evento)
admin.site.register(Evento, EventoAdmin)