
# Señales limpias y funcionales
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Participante, Asistente, AdministradorEvento
import secrets
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

@receiver(post_save, sender=Participante)
def participante_admitido_signal(sender, instance, created, **kwargs):
    # Solo si el estado es admitido
    if instance.estado == 'admitido':
        try:
            from inscripciones.models import InscripcionEvento
            from proyectos.utils import enviar_correo_admision_participante
            inscripcion = InscripcionEvento.objects.filter(usuario=instance.usuario, usuario__rol='participante').order_by('-id').first()
            evento = inscripcion.evento if inscripcion else None
            clave = inscripcion.clave_acceso if inscripcion else None
            if clave:
                enviar_correo_admision_participante(instance, evento, clave=clave)
        except Exception as e:
            print(f"Error enviando correo de admisión (señal): {e}")

@receiver(post_save, sender=Asistente)
def asistente_admitido_signal(sender, instance, created, **kwargs):
    if instance.estado == 'admitido':
        clave = getattr(instance.usuario, 'clave_temporal', None)
        if not clave:
            clave = secrets.token_urlsafe(8)
            instance.usuario.set_password(clave)
            instance.usuario.save()
            if hasattr(instance, 'clave_temporal'):
                instance.clave_temporal = clave
                instance.save()
        try:
            html_content = render_to_string('emails/bienvenida_asistente.html', {
                'usuario': instance.usuario,
                'clave_acceso': clave,
            })
            email = EmailMessage(
                subject="Bienvenido como Asistente",
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[instance.usuario.email],
            )
            email.content_subtype = 'html'
            email.send()
        except Exception as e:
            print(f"Error enviando correo a asistente admitido: {e}")

@receiver(post_save, sender=AdministradorEvento)
def admin_evento_admitido_signal(sender, instance, created, **kwargs):
    if instance.estado == 'admitido':
        clave = getattr(instance.usuario, 'clave_temporal', None)
        if not clave:
            clave = secrets.token_urlsafe(8)
            instance.usuario.set_password(clave)
            instance.usuario.save()
            if hasattr(instance, 'clave_temporal'):
                instance.clave_temporal = clave
                instance.save()
        try:
            html_content = render_to_string('emails/bienvenida_admin_evento.html', {
                'usuario': instance.usuario,
                'clave_acceso': clave,
            })
            email = EmailMessage(
                subject="Bienvenido como Administrador de Evento",
                body=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[instance.usuario.email],
            )
            email.content_subtype = 'html'
            email.send()
        except Exception as e:
            print(f"Error enviando correo a admin admitido: {e}")
