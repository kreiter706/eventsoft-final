from django.core.mail import EmailMessage
from django.conf import settings


def enviar_correo_admision_participante(participante, evento, representante=None, clave=None):
    """
    Envía un correo de admisión al participante con su clave de acceso y datos del representante.
    """
    nombre_participante = participante.usuario.first_name
    # Usar la clave pasada por argumento si existe, si no usar la del modelo
    clave_final = clave if clave else participante.clave_temporal
    nombre_evento = evento.nombre
    cuerpo = f"""
¡Admitido como participante!

Hola {nombre_participante},

¡Felicidades! Has sido admitido como participante en el evento {nombre_evento}.

Tu clave de acceso al sistema es: {clave_final}

"""
    if representante:
        cuerpo += f"El representante del proyecto es: {representante.usuario.first_name} ({representante.usuario.email})\n"
    cuerpo += "Adjunto encontrarás tu código QR de inscripción para presentar en el evento. ¡Te esperamos!"
    email = EmailMessage(
        subject=f"Admitido como participante en {nombre_evento}",
        body=cuerpo,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[participante.usuario.email],
    )
    # Aquí puedes adjuntar el QR si lo tienes generado
    email.send()
