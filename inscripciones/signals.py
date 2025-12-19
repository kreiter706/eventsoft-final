from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Participante, Asistente, Evaluador, AdministradorEvento
from .models import InscripcionEvento
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import qrcode
from io import BytesIO

@receiver(post_save, sender=InscripcionEvento)
def crear_objeto_rol_al_admitir(sender, instance, created, **kwargs):
    # Solo actuar si el estado es admitido
    if instance.estado == 'admitido':
        usuario = instance.usuario
        print(f"Signal ejecutado para usuario: {usuario.email} con rol: {usuario.rol}")
        if usuario.rol == 'participante':
            obj, _ = Participante.objects.get_or_create(usuario=usuario)
            obj.estado = 'admitido'
            obj.save()
        elif usuario.rol == 'asistente':
            obj, _ = Asistente.objects.get_or_create(usuario=usuario)
            obj.estado = 'admitido'
            obj.save()
        elif usuario.rol == 'evaluador':
            obj, _ = Evaluador.objects.get_or_create(usuario=usuario)
            obj.estado = 'admitido'
            obj.save()
        elif usuario.rol == 'admin_evento':
            obj, _ = AdministradorEvento.objects.get_or_create(usuario=usuario)
            obj.estado = 'admitido'
            obj.save()

@receiver(post_save, sender=InscripcionEvento)
def enviar_comprobante_asistente(sender, instance, created, **kwargs):
    if created and instance.usuario.rol == 'asistente':
        # Generar clave si no existe
        if not instance.clave_acceso:
            import secrets
            clave = secrets.token_urlsafe(8)
            instance.clave_acceso = clave
            instance.save()
        # Generar datos para el QR
        qr_data = f"InscripcionID:{instance.id}|Usuario:{instance.usuario.email}|Evento:{instance.evento.nombre}"
        qr = qrcode.make(qr_data)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        qr_content = qr_io.getvalue()

        # Renderizar comprobante (puedes mejorar con PDF)
        html_content = render_to_string('emails/comprobante_inscripcion.html', {
            'usuario': instance.usuario,
            'evento': instance.evento,
            'clave_acceso': instance.clave_acceso,
        })
        text_content = strip_tags(html_content)

        # Enviar correo
        email = EmailMessage(
            subject=f"Comprobante de inscripción a {instance.evento.nombre}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.usuario.email],
        )
        email.attach('qr.png', qr_content, 'image/png')
        email.content_subtype = 'html'
        email.send()

@receiver(post_save, sender=InscripcionEvento)
def notificar_participante_admision(sender, instance, created, **kwargs):
    usuario = instance.usuario
    if usuario.rol == 'participante':
        if instance.estado == 'admitido':
            # Generar clave si no existe
            if not instance.clave_acceso:
                import secrets
                clave = secrets.token_urlsafe(8)
                instance.clave_acceso = clave
                instance.save()
            # Generar QR
            qr_data = f"InscripcionID:{instance.id}|Usuario:{usuario.email}|Evento:{instance.evento.nombre}"
            qr = qrcode.make(qr_data)
            qr_io = BytesIO()
            qr.save(qr_io, format='PNG')
            qr_content = qr_io.getvalue()
            # Renderizar correo de admisión
            html_content = render_to_string('emails/admision_participante.html', {
                'usuario': usuario,
                'evento': instance.evento,
                'clave_acceso': instance.clave_acceso,
            })
            text_content = strip_tags(html_content)
            email = EmailMessage(
                subject=f"Admisión confirmada: {instance.evento.nombre}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            email.attach('qr.png', qr_content, 'image/png')
            email.content_subtype = 'html'
            email.send()
        elif instance.estado == 'no_admitido':
            # Renderizar correo de no admisión
            html_content = render_to_string('emails/no_admision_participante.html', {
                'usuario': usuario,
                'evento': instance.evento,
            })
            text_content = strip_tags(html_content)
            email = EmailMessage(
                subject=f"Resultado de inscripción: {instance.evento.nombre}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            email.content_subtype = 'html'
            email.send()

@receiver(post_save, sender=InscripcionEvento)
def notificar_evaluador_admision(sender, instance, created, **kwargs):
    usuario = instance.usuario
    if usuario.rol == 'evaluador':
        if instance.estado == 'admitido':
            # Generar clave si no existe
            if not instance.clave_acceso:
                import secrets
                clave = secrets.token_urlsafe(8)
                instance.clave_acceso = clave
                instance.save()
            html_content = render_to_string('emails/admision_evaluador.html', {
                'usuario': usuario,
                'evento': instance.evento,
                'clave_acceso': instance.clave_acceso,
            })
            text_content = strip_tags(html_content)
            email = EmailMessage(
                subject=f"Admisión como evaluador: {instance.evento.nombre}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            email.content_subtype = 'html'
            email.send()
        elif instance.estado == 'no_admitido':
            html_content = render_to_string('emails/no_admision_evaluador.html', {
                'usuario': usuario,
                'evento': instance.evento,
            })
            text_content = strip_tags(html_content)
            email = EmailMessage(
                subject=f"Resultado de inscripción como evaluador: {instance.evento.nombre}",
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[usuario.email],
            )
            email.content_subtype = 'html'
            email.send()