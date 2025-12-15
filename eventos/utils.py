from django.core.mail import send_mail
from django.conf import settings
from inscripciones.models import InscripcionEvento

def notificar_asistentes_evento(evento, asunto, mensaje):
    """
    Envía una notificación por email a todos los asistentes inscritos en el evento.
    """
    inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente', estado='admitido')
    destinatarios = [i.usuario.email for i in inscripciones]
    if destinatarios:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
        )
