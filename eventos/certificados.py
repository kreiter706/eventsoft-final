from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings

def generar_certificado_asistencia(asistente, evento):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-100, "Certificado de Asistencia")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-150, f"Se certifica que {asistente.usuario.first_name} {asistente.usuario.last_name}")
    c.drawCentredString(width/2, height-180, f"asistió al evento: {evento.nombre}")
    c.drawCentredString(width/2, height-210, f"Fecha: {evento.fecha_inicio} al {evento.fecha_fin}")
    c.drawCentredString(width/2, height-240, f"Lugar: {evento.lugar}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height-300, "¡Felicitaciones por tu participación!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def enviar_certificado_asistencia(asistente, evento):
    pdf_buffer = generar_certificado_asistencia(asistente, evento)
    email = EmailMessage(
        subject=f"Certificado de Asistencia - {evento.nombre}",
        body=f"Adjunto encontrarás tu certificado de asistencia al evento {evento.nombre}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[asistente.usuario.email],
    )
    email.attach(f"certificado_{evento.nombre}.pdf", pdf_buffer.read(), 'application/pdf')
    email.send()
