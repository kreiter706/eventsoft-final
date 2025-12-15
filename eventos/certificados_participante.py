from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings

def generar_certificado_participacion(participante, evento):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-100, "Certificado de Participación")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-150, f"Se certifica que {participante.usuario.first_name} {participante.usuario.last_name}")
    c.drawCentredString(width/2, height-180, f"participó en el evento: {evento.nombre}")
    c.drawCentredString(width/2, height-210, f"Fecha: {evento.fecha_inicio} al {evento.fecha_fin}")
    c.drawCentredString(width/2, height-240, f"Lugar: {evento.lugar}")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height-300, "¡Felicitaciones por tu participación!")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def enviar_certificado_participacion(participante, evento):
    pdf_buffer = generar_certificado_participacion(participante, evento)
    email = EmailMessage(
        subject=f"Certificado de Participación - {evento.nombre}",
        body=f"Adjunto encontrarás tu certificado de participación en el evento {evento.nombre}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[participante.usuario.email],
    )
    email.attach(f"certificado_participacion_{evento.nombre}.pdf", pdf_buffer.read(), 'application/pdf')
    email.send()
