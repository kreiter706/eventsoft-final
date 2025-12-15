from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import EvaluadorEvento
from django.core.mail import send_mail

@receiver(post_save, sender=EvaluadorEvento)
def notificar_estado_evaluador(sender, instance, created, **kwargs):
    if not created:
        if instance.estado == 'admitido':
            send_mail(
                'Admitido como evaluador',
                f'Has sido admitido como evaluador en el evento {instance.evento.nombre}.',
                'noreply@tusitio.com',
                [instance.evaluador.usuario.email],
            )
        elif instance.estado == 'rechazado':
            send_mail(
                'No admitido como evaluador',
                f'No has sido admitido como evaluador en el evento {instance.evento.nombre}.',
                'noreply@tusitio.com',
                [instance.evaluador.usuario.email],
            )