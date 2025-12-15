from django.urls import reverse
# Vista para mostrar opciones de participación antes de preinscribirse
def opciones_participacion(request, evento_id):
    url_individual = reverse('preinscripcion_participante', args=[evento_id])
    url_grupal = reverse('registrar_proyecto', args=[evento_id])
    return render(request, 'eventos/opciones_participacion.html', {
        'evento': get_object_or_404(Evento, id=evento_id),
        'url_individual': url_individual,
        'url_grupal': url_grupal,
    })
# IMPORTS AL INICIO
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Vista para eliminar memorias seleccionadas
@login_required
@csrf_exempt
def eliminar_memorias(request):
    if not request.user.is_authenticated or getattr(request.user, 'rol', None) != 'admin':
        return HttpResponse('No tienes permisos para eliminar memorias.', status=403)
    if request.method == 'POST':
        archivos = request.POST.getlist('archivos')
        import os
        from django.conf import settings
        ruta_memorias = os.path.join(settings.MEDIA_ROOT, 'info_tecnica_evento')
        eliminados = []
        for archivo in archivos:
            ruta = os.path.join(ruta_memorias, archivo)
            if os.path.exists(ruta):
                os.remove(ruta)
                eliminados.append(archivo)
        if eliminados:
            messages.success(request, f"Se eliminaron: {', '.join(eliminados)}")
        else:
            messages.info(request, "No se eliminaron archivos.")
    return redirect('memorias_evento')
# Vista para listar todos los eventos y acceder a la habilitación/deshabilitación de inscripciones por rol
@login_required
def habilitar_inscripciones_eventos(request):
    eventos = Evento.objects.all().order_by('-fecha_inicio')
    return render(request, 'eventos/habilitar_inscripciones_eventos.html', {'eventos': eventos})

# Vista para editar la habilitación/deshabilitación de inscripciones por rol para un evento
@login_required
def habilitar_inscripciones_rol(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.inscripciones_participante = 'inscripciones_participante' in request.POST
        evento.inscripciones_evaluador = 'inscripciones_evaluador' in request.POST
        evento.inscripciones_asistente = 'inscripciones_asistente' in request.POST
        evento.save()
        messages.success(request, 'Cambios guardados correctamente.')
        return redirect(reverse('habilitar_inscripciones_eventos'))
    return render(request, 'eventos/habilitar_inscripciones_rol.html', {'evento': evento})
from django.http import HttpResponse

def calificar_participantes_evento(request, evento_id):
    evaluador = getattr(request.user, 'evaluador', None)
    if not evaluador:
        return redirect('inicio_roles')
    if not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id).exists():
        return redirect('eventos_asignados_evaluador')
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante
    inscripciones = InscripcionEvento.objects.filter(evento_id=evento_id, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    instrumentos = InstrumentoEvaluacion.objects.filter(evento_id=evento_id)
    return render(request, 'eventos/calificar_participantes_evento.html', {
        'evento_id': evento_id,
        'participantes': participantes,
        'instrumentos': instrumentos
    })
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
# ...existing code...

def enviar_certificado_reconocimiento(participante, evento, puesto):
    """
    Envía el certificado de reconocimiento al participante destacado por email.
    """
    # Obtener configuración personalizada
    try:
        config = evento.configuracion_certificado
    except Exception:
        config = None

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height-100, "Certificado de Reconocimiento")
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-150, f"Se certifica que {participante.usuario.first_name} {participante.usuario.last_name}")
    c.drawCentredString(width/2, height-180, f"obtuvo el puesto {puesto} en el evento: {evento.nombre}")
    if config:
        # Usar datos personalizados si existen
        fecha_inicio = config.fecha_inicio_evento.strftime('%d/%m/%Y') if config.fecha_inicio_evento else str(evento.fecha_inicio)
        fecha_fin = config.fecha_fin_evento.strftime('%d/%m/%Y') if config.fecha_fin_evento else str(evento.fecha_fin)
        c.drawCentredString(width/2, height-210, f"Fecha: {fecha_inicio} al {fecha_fin}")
        c.drawCentredString(width/2, height-240, f"Lugar: {config.lugar_evento}")
        c.setFont("Helvetica", 12)
        mensaje = config.mensaje_certificado if config.mensaje_certificado else "¡Felicitaciones por tu logro destacado!"
        c.drawCentredString(width/2, height-300, mensaje)
    else:
        c.drawCentredString(width/2, height-210, f"Fecha: {evento.fecha_inicio} al {evento.fecha_fin}")
        c.drawCentredString(width/2, height-240, f"Lugar: {evento.lugar}")
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height-300, "¡Felicitaciones por tu logro destacado!")
    c.showPage()
    c.save()
    buffer.seek(0)
    email = EmailMessage(
        subject=f"Certificado de Reconocimiento - {evento.nombre}",
        body=f"Adjunto encontrarás tu certificado de reconocimiento por tu puesto destacado en el evento {evento.nombre}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[participante.usuario.email],
    )
    email.attach(f"certificado_reconocimiento_{evento.nombre}_puesto{puesto}.pdf", buffer.read(), 'application/pdf')
    email.send()
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.http import FileResponse, Http404
import os
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from datetime import date
from .forms import PreinscripcionEvaluadorForm
from .forms import InfoTecnicaEventoForm
from .models import InfoTecnicaEvento
from documentos.models import DocumentoParticipante
from documentos.models import DocumentoParticipante
from django.conf import settings
from .models import Evento, InstrumentoEvaluacion, ItemInstrumento, EvaluadorEvento
from .forms import (
    PreinscripcionParticipanteForm,
    EventoForm,
    RegistroVisitanteEventoForm,
    
    RegistroAsistenteEventoForm,
    ItemInstrumentoForm,
    InstrumentoEvaluacionForm
)
from usuarios.models import Usuario, Evaluador, Participante
from inscripciones.models import InscripcionEvento
from documentos.models import DocumentoParticipante
from evaluaciones.models import CalificacionParticipante
from evaluaciones.forms import CalificacionParticipanteForm
import qrcode
from io import BytesIO
import os
from reportlab.pdfgen import canvas
from django import forms
from django.db.models import Sum
from django.contrib import messages
import csv
from django.http import HttpResponse
# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\views.py
# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\views.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def descargar_programacion_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    usuario = request.user

    # Verificar si el usuario tiene una inscripción admitida en el evento
    inscripcion = InscripcionEvento.objects.filter(usuario=usuario, evento=evento, estado='admitido').first()
    if not inscripcion:
        messages.error(request, "No tienes permiso para descargar la programación.")
        return redirect('detalle_evento', evento_id=evento_id)

    # Obtener las actividades del evento
    actividades = evento.programaciones.all()
    if not actividades.exists():
        messages.error(request, "No hay actividades programadas para este evento.")
        return redirect('detalle_evento', evento_id=evento_id)

    # Generar el archivo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="programacion_{evento.nombre}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Programación del evento: {evento.nombre}")
    y = 770
    for actividad in actividades:
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y, f"Título: {actividad.titulo_actividad}")
        y -= 15
        p.setFont("Helvetica", 10)
        p.drawString(100, y, f"Descripción: {actividad.descripcion}")
        y -= 15
        p.drawString(100, y, f"Fecha: {actividad.fecha} | Hora: {actividad.hora_inicio} - {actividad.hora_fin} | Lugar: {actividad.lugar}")
        y -= 30
        if y < 50:
            p.showPage()

            y = 800
    p.save()
    return response

# Import necesario para login_required
from django.contrib.auth.decorators import login_required

@login_required
def mis_inscripciones(request):
    inscripciones = InscripcionEvento.objects.filter(usuario=request.user)
    return render(request, 'eventos/mis_inscripciones.html', {'inscripciones': inscripciones})

def memorias_evento(request):
    """
    Vista para listar las memorias (archivos) disponibles para descargar de un evento.
    """
    import os
    from django.conf import settings
    # Eliminada la funcionalidad de redirección por múltiples clics
    ruta_memorias = os.path.join(settings.MEDIA_ROOT, 'info_tecnica_evento')
    try:
        archivos = os.listdir(ruta_memorias)
        archivos = [f for f in archivos if os.path.isfile(os.path.join(ruta_memorias, f))]
    except FileNotFoundError:
        archivos = []
    return render(request, 'eventos/memorias_evento.html', {'archivos': archivos})

def descargar_memoria(request, filename):
    """
    Descarga un archivo de memorias del evento.
    """
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'info_tecnica_evento', filename)
    if os.path.exists(ruta_archivo):
        return FileResponse(open(ruta_archivo, 'rb'), as_attachment=True, filename=filename)
    else:
        raise Http404('Archivo no encontrado')
    
def eventos_proximos(request):
    from .models import Categoria
    nombre = request.GET.get('nombre', '')
    categoria_id = request.GET.get('categoria', '')
    eventos = Evento.objects.filter(fecha_inicio__gte=date.today(), estado='aceptado')  # Filtrar solo eventos aceptados
    if nombre:
        eventos = eventos.filter(nombre__icontains=nombre)
    if categoria_id:
        eventos = eventos.filter(categoria_id=categoria_id)
    eventos = eventos.order_by('fecha_inicio')
    categorias = Categoria.objects.all()
    return render(request, 'eventos/eventos_proximos.html', {
        'eventos': eventos,
        'categorias': categorias,
        'nombre': nombre,
        'categoria_id': categoria_id
    })

def buscar_eventos(request):
    query = request.GET.get('q', '')
    eventos = Evento.objects.all()
    if query:
        eventos = eventos.filter(nombre__icontains=query)
    return render(request, 'eventos/buscar_eventos.html', {'eventos': eventos, 'query': query})

def detalle_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    return render(request, 'eventos/detalle_evento.html', {'evento': evento})

def crear_evento(request):
    # Solo permitir acceso a usuarios con rol admin o superadmin
    from django.shortcuts import redirect
    if not request.user.is_authenticated:
        return redirect('/usuarios/login')
    if not hasattr(request.user, 'rol') or request.user.rol not in ['admin', 'superadmin']:
        return redirect('/usuarios/login')

    from usuarios.models_codigo_acceso import EventAdminAccessCode
    from django.contrib import messages

    # Validar límite de eventos solo para admin (no superadmin)
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        try:
            access_code = request.user.event_access_code
            if access_code.max_events is not None:
                eventos_creados = request.user.eventos_creados.filter(estado__in=['pendiente', 'aceptado']).count()
                if eventos_creados >= access_code.max_events:
                    messages.error(request, f'Has alcanzado el máximo de eventos que puedes crear ({access_code.max_events}). Si necesitas crear más, contacta al superadministrador.')
                    return render(request, 'eventos/crear_evento.html', {'form': EventoForm(), 'eventos_creados': eventos_creados, 'max_events': access_code.max_events})
        except EventAdminAccessCode.DoesNotExist:
            pass

    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            import logging
            logger = logging.getLogger('django')
            logger.warning(f"[DEBUG] Antes de asignar creador: evento.creador_id={evento.creador_id}")
            evento.creador = request.user
            logger.warning(f"[DEBUG] Después de asignar creador: evento.creador_id={evento.creador_id}, user_id={request.user.id}")
            # Si el usuario es admin, el evento queda pendiente para aprobación
            if hasattr(request.user, 'rol') and request.user.rol == 'admin':
                evento.estado = 'pendiente'
            evento.save()
            logger.warning(f"[DEBUG] Evento guardado: evento.id={evento.id}, evento.creador_id={evento.creador_id}")
            form.save_m2m()
            # Guardar mensaje en la sesión para mostrarlo en inicio_admin
            request.session['evento_creado_pendiente'] = True
            return redirect('/usuarios/admin/')
    else:
        form = EventoForm()
    # Mostrar al admin el número de eventos creados y el máximo permitido
    eventos_creados = 0
    max_events = None
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        try:
            access_code = request.user.event_access_code
            max_events = access_code.max_events
            eventos_creados = request.user.eventos_creados.filter(estado__in=['pendiente', 'aceptado']).count()
        except EventAdminAccessCode.DoesNotExist:
            pass
    return render(request, 'eventos/crear_evento.html', {'form': form, 'eventos_creados': eventos_creados, 'max_events': max_events})

def editar_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('inicio_admin')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/editar_evento.html', {'form': form, 'evento': evento})

def registro_visitante_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = RegistroVisitanteEventoForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            soporte_pago = form.cleaned_data['soporte_pago']
            usuario, creado = Usuario.objects.get_or_create(
                username=correo,
                defaults={'email': correo, 'first_name': nombre}
            )
            InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
            if soporte_pago:
                ruta = os.path.join(settings.MEDIA_ROOT, 'soportes_pago')
                os.makedirs(ruta, exist_ok=True)
                nombre_archivo = f"{correo}_{evento_id}_{soporte_pago.name}"
                with open(os.path.join(ruta, nombre_archivo), 'wb+') as destino:
                    for chunk in soporte_pago.chunks():
                        destino.write(chunk)
            return render(request, 'eventos/registro_exitoso.html', {'evento': evento})
    else:
        form = RegistroVisitanteEventoForm()
    return render(request, 'eventos/registro_visitante.html', {'form': form, 'evento': evento})

def registro_asistente_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    mensaje = None
    if not evento.inscripciones_asistente:
        mensaje = "Las inscripciones para asistentes en este evento están deshabilitadas."
        return render(request, 'eventos/registro_asistente.html', {'form': None, 'evento': evento, 'mensaje': mensaje})
    if request.method == 'POST':
        form = RegistroAsistenteEventoForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            password = form.cleaned_data['password']
            documento = form.cleaned_data.get('documento')
            usuario = Usuario.objects.filter(username=correo).first() or Usuario.objects.filter(email=correo).first()
            if usuario:
                user = authenticate(request, username=usuario.username, password=password)
                if user:
                    if not user.rol or user.rol != 'asistente':
                        user.rol = 'asistente'
                        user.save()
                        login(request, user, backend='usuarios.backends.EmailOrUsernameModelBackend')
                    inscripcion, _ = InscripcionEvento.objects.get_or_create(usuario=user, evento=evento)
                    if documento:
                        DocumentoParticipante.objects.create(
                            inscripcion=inscripcion,
                            archivo=documento,
                            descripcion="Documento de inscripción"
                        )
                    return render(request, 'eventos/registro_exitoso.html', {'evento': evento})
                else:
                    form.add_error(None, "Correo o contraseña incorrectos.")
            else:
                usuario = Usuario.objects.create_user(
                    username=correo,
                    email=correo,
                    first_name=nombre,
                    password=password
                )
                usuario.rol = 'asistente'
                usuario.save()
                login(request, usuario, backend='usuarios.backends.EmailOrUsernameModelBackend')
                inscripcion, _ = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
                if documento:
                    DocumentoParticipante.objects.create(
                        inscripcion=inscripcion,
                        archivo=documento,
                        descripcion="Documento de inscripción"
                    )
                return render(request, 'eventos/registro_exitoso.html', {'evento': evento})
    else:
        form = RegistroAsistenteEventoForm()
    return render(request, 'eventos/registro_asistente.html', {'form': form, 'evento': evento})

def preinscripcion_participante(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    mensaje = None
    if not evento.inscripciones_participante:
        mensaje = "Las inscripciones para participantes en este evento están deshabilitadas."
        return render(request, 'eventos/preinscripcion_participante.html', {'form': None, 'evento': evento, 'mensaje': mensaje})
    if request.method == 'POST':
        form = PreinscripcionParticipanteForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            documento = form.cleaned_data['documento']
            comprobante_pago = form.cleaned_data.get('comprobante_pago')
            usuario = Usuario.objects.filter(email=correo).first()
            if not usuario:
                usuario = Usuario(
                    email=correo,
                    username=correo,
                    first_name=nombre
                )
                usuario.set_password(form.cleaned_data['password'])
                usuario.rol = 'participante'
                usuario.save()
            else:
                if usuario.rol != 'participante':
                    usuario.rol = 'participante'
                    usuario.save()
            inscripcion, creada = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
            import secrets
            clave_generada = secrets.token_urlsafe(8)
            usuario.set_password(clave_generada)
            usuario.save()
            if not creada:
                mensaje = f"¡Preinscripción exitosa!\n\nTu clave de acceso es: {clave_generada}\n\nGuárdala en un lugar seguro."
            else:
                DocumentoParticipante.objects.create(
                    inscripcion=inscripcion,
                    archivo=documento,
                    descripcion="Documento de preinscripción"
                )
                # Guardar comprobante de pago solo si el evento tiene costo y se subió el archivo
                if evento.costo_inscripcion and comprobante_pago:
                    DocumentoParticipante.objects.create(
                        inscripcion=inscripcion,
                        archivo=comprobante_pago,
                        descripcion="Comprobante de pago"
                    )
                mensaje = f"¡Preinscripción exitosa!\n\nTu clave de acceso es: {clave_generada}\n\nGuárdala en un lugar seguro."
            return render(request, 'eventos/preinscripcion_exitosa.html', {'evento': evento, 'mensaje': mensaje})
    else:
        form = PreinscripcionParticipanteForm()
    return render(request, 'eventos/preinscripcion_participante.html', {'form': form, 'evento': evento})

@login_required
def instrumentos_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    instrumentos = evento.instrumentos.all()
    return render(request, 'eventos/instrumentos_evento.html', {
        'evento': evento,
        'instrumentos': instrumentos
    })

@login_required
def eventos_asignados_evaluador(request):
    evaluador = getattr(request.user, 'evaluador', None)
    if not evaluador:
        return redirect('inicio_roles')
    eventos = Evento.objects.filter(evaluadores_asignados__evaluador=evaluador)
    return render(request, 'eventos/eventos_asignados_evaluador.html', {'eventos': eventos})

@login_required
def gestionar_items_instrumento(request, evento_id, instrumento_id):
    evaluador = getattr(request.user, 'evaluador', None)
    if not evaluador:
        return redirect('inicio_roles')
    # Verificar que el evaluador esté asignado a este evento
    if not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id).exists():
        return redirect('eventos_asignados_evaluador')
    instrumento = get_object_or_404(InstrumentoEvaluacion, id=instrumento_id, evento_id=evento_id)
    items = ItemInstrumento.objects.filter(instrumento=instrumento)
    # Obtener participantes admitidos del evento
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante
    inscripciones = InscripcionEvento.objects.filter(evento_id=evento_id, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    if request.method == 'POST':
        form = ItemInstrumentoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.instrumento = instrumento
            item.save()
            return redirect('gestionar_items_instrumento', evento_id=evento_id, instrumento_id=instrumento_id)
    else:
        form = ItemInstrumentoForm()
    return render(request, 'eventos/gestionar_items_instrumento.html', {
        'instrumento': instrumento,
        'items': items,
        'form': form,
        'evento_id': evento_id,
        'participantes': participantes
    })

@login_required
def editar_item_instrumento(request, evento_id, instrumento_id, item_id):
    evaluador = getattr(request.user, 'evaluador', None)
    if not evaluador or not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id).exists():
        return redirect('eventos_asignados_evaluador')
    item = get_object_or_404(ItemInstrumento, id=item_id, instrumento_id=instrumento_id)
    if request.method == 'POST':
        form = ItemInstrumentoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('gestionar_items_instrumento', evento_id=evento_id, instrumento_id=instrumento_id)
    else:
        form = ItemInstrumentoForm(instance=item)
    return render(request, 'eventos/editar_item_instrumento.html', {'form': form, 'item': item, 'instrumento_id': instrumento_id, 'evento_id': evento_id})

@login_required
def eliminar_item_instrumento(request, evento_id, instrumento_id, item_id):
    evaluador = getattr(request.user, 'evaluador', None)
    if not evaluador or not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id).exists():
        return redirect('eventos_asignados_evaluador')
    item = get_object_or_404(ItemInstrumento, id=item_id, instrumento_id=instrumento_id)
    if request.method == 'POST':
        item.delete()
        return redirect('gestionar_items_instrumento', evento_id=evento_id, instrumento_id=instrumento_id)
    return render(request, 'eventos/eliminar_item_instrumento.html', {'item': item, 'instrumento_id': instrumento_id, 'evento_id': evento_id})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from evaluaciones.models import CalificacionParticipante
from eventos.models import InstrumentoEvaluacion, ItemInstrumento, Evento
from usuarios.models import Participante

class CalificacionParticipanteForm(forms.ModelForm):
    class Meta:
        model = CalificacionParticipante
        fields = ['puntaje', 'observaciones']
        widgets = {
            'puntaje': forms.NumberInput(attrs={'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={'rows': 2}),
        }

@login_required
def calificar_participante(request, evento_id, instrumento_id, participante_id):
    evaluador = getattr(request.user, 'evaluador', None)
    if not evaluador or not Evento.objects.filter(id=evento_id, evaluadores_asignados__evaluador=evaluador).exists():
        return redirect('eventos_asignados_evaluador')

    instrumento = get_object_or_404(InstrumentoEvaluacion, id=instrumento_id, evento_id=evento_id)
    participante = get_object_or_404(Participante, id=participante_id)
    items = ItemInstrumento.objects.filter(instrumento=instrumento)

    # Crear un formulario dinámico para cada ítem
    forms_dict = {}
    for item in items:
        calificacion, created = CalificacionParticipante.objects.get_or_create(
            evaluador=evaluador,
            participante=participante,
            evento_id=evento_id,
            instrumento=instrumento,
            item=item,
            defaults={'puntaje': 0}
        )
        forms_dict[item.id] = CalificacionParticipanteForm(instance=calificacion, prefix=f"item_{item.id}")

    if request.method == 'POST':
        valid = True
        for item_id, form in forms_dict.items():
            form = CalificacionParticipanteForm(request.POST, instance=form.instance, prefix=f"item_{item_id}")
            if form.is_valid():
                puntaje = form.cleaned_data['puntaje']
                if puntaje > form.instance.item.puntaje_maximo:  # Validación del límite de puntaje
                    valid = False
                    form.add_error('puntaje', f"El puntaje no puede superar el límite de {form.instance.item.puntaje_maximo}.")
                else:
                    form.save()
            else:
                valid = False

        if valid:
            messages.success(request, "Calificaciones guardadas correctamente.")
            return redirect('calificar_participantes_evento', evento_id=evento_id)
        else:
            messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")

    return render(request, 'eventos/calificar_participante.html', {
        'forms_dict': forms_dict,
        'participante': participante,
        'instrumento': instrumento,
        'evento_id': evento_id
    })

# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\views.py
@login_required
def ranking_evento(request, evento_id):
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante
    from evaluaciones.models import CalificacionParticipante
    evento = get_object_or_404(Evento, id=evento_id)

    # Participantes admitidos
    inscripciones = InscripcionEvento.objects.filter(evento=evento, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])

    # Calcular puntaje total ponderado por participante
    ranking = []
    for participante in participantes:
        puntaje_total = 0
        calificaciones = CalificacionParticipante.objects.filter(evento=evento, participante=participante)

        for calificacion in calificaciones:
            # Multiplicar el puntaje por el peso porcentaje del ítem
            puntaje_total += calificacion.puntaje * (calificacion.item.peso_porcentaje / 100)

        ranking.append({
            'participante': participante,
            'puntaje_total': round(puntaje_total, 2)  # Redondear a 2 decimales
        })

    # Ordenar el ranking por puntaje total de mayor a menor
    ranking = sorted(ranking, key=lambda x: x['puntaje_total'], reverse=True)

    # Agregar posición al ranking
    for idx, item in enumerate(ranking, start=1):
        item['posicion'] = idx

    # El envío de certificados a los 3 primeros ahora es manual mediante botón
    enviados = False
    if request.method == 'POST' and 'enviar_certificados' in request.POST:
        for idx, item in enumerate(ranking[:3], 1):
            participante = item['participante']
            enviar_certificado_reconocimiento(participante, evento, idx)
        enviados = True

    return render(request, 'eventos/ranking_evento.html', {
        'evento': evento,
        'ranking': ranking,
        'enviados': enviados
    })

@login_required
def comparativa_calificaciones_evento(request, evento_id):
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante, Evaluador
    from evaluaciones.models import CalificacionParticipante
    evento = get_object_or_404(Evento, id=evento_id)
    instrumentos = evento.instrumentos.all()
    inscripciones = InscripcionEvento.objects.filter(evento=evento, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    evaluadores = Evaluador.objects.filter(eventos_asignados__evento=evento).distinct()
    # Estructura: {participante: {instrumento: {item: {evaluador: puntaje}}}}
    comparativa = {}
    for participante in participantes:
        comparativa[participante] = {}
        for instrumento in instrumentos:
            comparativa[participante][instrumento] = {}
            for item in instrumento.items.all():
                comparativa[participante][instrumento][item] = {}
                for evaluador in evaluadores:
                    calif = CalificacionParticipante.objects.filter(
                        evento=evento,
                        instrumento=instrumento,
                        item=item,
                        participante=participante,
                        evaluador=evaluador
                    ).first()
                    comparativa[participante][instrumento][item][evaluador] = calif.puntaje if calif else None
    return render(request, 'eventos/comparativa_calificaciones_evento.html', {
        'evento': evento,
        'instrumentos': instrumentos,
        'participantes': participantes,
        'evaluadores': evaluadores,
        'comparativa': comparativa
    })

from django.core.exceptions import ValidationError
# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import InstrumentoEvaluacion, ItemInstrumento
from .forms import ItemInstrumentoForm

# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\eventos\views.py
@login_required
def gestionar_items_instrumento(request, evento_id, instrumento_id):
    instrumento = get_object_or_404(InstrumentoEvaluacion, id=instrumento_id, evento_id=evento_id)
    items = ItemInstrumento.objects.filter(instrumento=instrumento)

    if request.method == 'POST':
        form = ItemInstrumentoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.instrumento = instrumento  # Asignar el instrumento al ítem
            try:
                item.save()  # Esto ejecuta la validación en el modelo
                messages.success(request, "Ítem agregado correctamente.")
                return redirect('gestionar_items_instrumento', evento_id=evento_id, instrumento_id=instrumento_id)
            except ValidationError as e:
                # Agregar el error al formulario para mostrarlo en el HTML
                form.add_error(None, e.message)
        else:
            messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")
    else:
        form = ItemInstrumentoForm()

    return render(request, 'eventos/gestionar_items_instrumento.html', {
        'instrumento': instrumento,
        'items': items,
        'form': form,
        'evento_id': evento_id,
    })

@login_required
def admin_crear_instrumento(request, evento_id):
    from django.contrib import messages
    if not request.user.is_authenticated or request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_roles')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = InstrumentoEvaluacionForm(request.POST, request.FILES)
        if form.is_valid():
            instrumento = form.save(commit=False)
            instrumento.evento = evento
            instrumento.save()
            messages.success(request, "Instrumento creado correctamente.")
            return redirect('eventos_gestion_instrumentos_admin')
    else:
        form = InstrumentoEvaluacionForm()
    return render(request, 'eventos/admin_crear_instrumento.html', {'form': form, 'evento': evento})

@login_required
def admin_tabla_posiciones(request, evento_id):
    if not request.user.is_authenticated or request.user.rol != 'admin':
        from django.contrib import messages
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_roles')
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante
    from evaluaciones.models import CalificacionParticipante
    from django.db.models import Sum
    evento = get_object_or_404(Evento, id=evento_id)
    inscripciones = InscripcionEvento.objects.filter(evento=evento, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    ranking = []
    for participante in participantes:
        puntaje_total = CalificacionParticipante.objects.filter(
            evento=evento,
            participante=participante
        ).aggregate(total=Sum('puntaje'))['total'] or 0
        ranking.append({
            'participante': participante,
            'puntaje_total': puntaje_total
        })
    ranking = sorted(ranking, key=lambda x: x['puntaje_total'], reverse=True)
    # Descarga CSV
    if request.GET.get('descargar') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=tabla_posiciones_{evento.nombre}.csv'
        writer = csv.writer(response)
        writer.writerow(['Posición', 'Nombre', 'Email', 'Puntaje total'])
        for idx, item in enumerate(ranking, 1):
            writer.writerow([
                idx,
                f"{item['participante'].usuario.first_name} {item['participante'].usuario.last_name}",
                item['participante'].usuario.email,
                item['puntaje_total']
            ])
        return response
    return render(request, 'eventos/admin_tabla_posiciones.html', {
        'evento': evento,
        'ranking': ranking
    })

@login_required
def admin_detalle_calificaciones_participante(request, evento_id, participante_id):
    if not request.user.is_authenticated or request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_roles')
    evento = get_object_or_404(Evento, id=evento_id)
    participante = get_object_or_404(Participante, id=participante_id)
    instrumentos = evento.instrumentos.all()
    from evaluaciones.models import CalificacionParticipante
    from usuarios.models import Evaluador
    detalle = []
    for instrumento in instrumentos:
        items = instrumento.items.all()
        for item in items:
            calificaciones = CalificacionParticipante.objects.filter(
                evento=evento,
                instrumento=instrumento,
                item=item,
                participante=participante
            )
            for calificacion in calificaciones:
                detalle.append({
                    'instrumento': instrumento,
                    'item': item,
                    'evaluador': calificacion.evaluador,
                    'puntaje': calificacion.puntaje
                })
    # Agrupar por instrumento e ítem para mostrar en el template
    from collections import defaultdict
    agrupado = defaultdict(lambda: defaultdict(list))
    for d in detalle:
        agrupado[d['instrumento']][d['item']].append({
            'evaluador': d['evaluador'],
            'puntaje': d['puntaje']
        })
    return render(request, 'eventos/admin_detalle_calificaciones_participante.html', {
        'evento': evento,
        'participante': participante,
        'agrupado': agrupado
    })

#----------------------------------------------------------------Evaluador--------------------------------------  # O crea un modelo específico si lo prefieres
import secrets

def preinscripcion_evaluador(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    mensaje = None
    clave_generada = None
    if not evento.inscripciones_evaluador:
        mensaje = "Las inscripciones para evaluadores en este evento están deshabilitadas."
        return render(request, 'eventos/preinscripcion_evaluador.html', {'form': None, 'evento': evento, 'mensaje': mensaje})
    if request.method == 'POST':
        form = PreinscripcionEvaluadorForm(request.POST, request.FILES)
        if form.is_valid():
            nombre = form.cleaned_data['nombre']
            correo = form.cleaned_data['correo']
            password = form.cleaned_data['password']
            documento = form.cleaned_data['documento']
            usuario = Usuario.objects.filter(email=correo).first()
            nueva_clave = secrets.token_urlsafe(8)
            if not usuario:
                # Usuario nuevo: genera clave aleatoria
                usuario = Usuario(
                    email=correo,
                    username=correo,
                    first_name=nombre
                )
                usuario.set_password(nueva_clave)
                usuario.rol = 'evaluador'
                usuario.save()
                clave_generada = nueva_clave
            else:
                usuario.rol = 'evaluador'
                usuario.set_password(nueva_clave)  # SIEMPRE genera nueva clave
                usuario.save()
                clave_generada = nueva_clave
            evaluador, _ = Evaluador.objects.get_or_create(usuario=usuario)
            rel, creada = EvaluadorEvento.objects.get_or_create(evaluador=evaluador, evento=evento)
            from inscripciones.models import InscripcionEvento
            inscripcion, _ = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
            if not creada:
                mensaje = "Ya estás preinscrito como evaluador en este evento."
            else:
                DocumentoParticipante.objects.create(
                    inscripcion=inscripcion,
                    archivo=documento,
                    descripcion="Documento de preinscripción evaluador"
                )
                mensaje = "¡Preinscripción exitosa!"
            return render(request, 'eventos/preinscripcion_exitosa.html', {
                'evento': evento,
                'mensaje': mensaje,
                'clave_generada': clave_generada
            })
    else:
        form = PreinscripcionEvaluadorForm()
    return render(request, 'eventos/registro_evaluador.html', {'form': form, 'evento': evento, 'mensaje': mensaje})

@login_required
def editar_preinscripcion_evaluador(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    usuario = request.user
    inscripcion, _ = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
    documento = DocumentoParticipante.objects.filter(inscripcion=inscripcion).first()
    if request.method == 'POST':
        form = PreinscripcionEvaluadorForm(request.POST, request.FILES, initial={
            'nombre': usuario.first_name,
            'correo': usuario.email,
        })
        if form.is_valid():
            usuario.first_name = form.cleaned_data['nombre']
            usuario.email = form.cleaned_data['correo']
            usuario.save()
            nuevo_doc = form.cleaned_data.get('documento')
            if nuevo_doc:
                if documento:
                    documento.archivo = nuevo_doc
                    documento.save()
                else:
                    if inscripcion is not None:
                        DocumentoParticipante.objects.create(
                            inscripcion=inscripcion,
                            archivo=nuevo_doc,
                            descripcion="Documento de preinscripción evaluador"
                        )
                    else:
                        messages.error(request, "No se encontró inscripción válida para este evento.")
                        return redirect('detalle_evento', evento_id=evento.id)
            return redirect('detalle_evento', evento_id=evento.id)
    else:
        form = PreinscripcionEvaluadorForm(initial={
            'nombre': usuario.first_name,
            'correo': usuario.email,
        })
    return render(request, 'eventos/editar_preinscripcion_evaluador.html', {
        'form': form,
        'evento': evento,
        'documento': documento
    })

from django.contrib import messages

@login_required
def cancelar_preinscripcion_evaluador(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id)
    usuario = request.user

    # Elimina la relación EvaluadorEvento
    evaluador = getattr(usuario, 'evaluador', None)
    if evaluador:
        EvaluadorEvento.objects.filter(evaluador=evaluador, evento=evento).delete()

    # Elimina inscripción y documentos asociados
    inscripcion = InscripcionEvento.objects.filter(usuario=usuario, evento=evento).first()
    if inscripcion:
        DocumentoParticipante.objects.filter(inscripcion=inscripcion).delete()
        inscripcion.delete()

    messages.success(request, "Has cancelado tu preinscripción como evaluador en este evento.")
    return redirect('eventos_asignados_evaluador')

@login_required
def lista_participantes_evaluador(request, evento_id):
    usuario = request.user
    evaluador = getattr(usuario, 'evaluador', None)
    if not evaluador or not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id, estado='admitido').exists():
        return HttpResponse("No tienes permiso para ver los participantes de este evento.", status=403)
    inscripciones = InscripcionEvento.objects.filter(evento_id=evento_id, estado='admitido', usuario__rol='participante')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    evento = Evento.objects.get(id=evento_id)
    return render(request, 'eventos/lista_participantes_evaluador.html', {
        'participantes': participantes,
        'evento': evento,
        'total': participantes.count()
    })


@login_required
def detalle_participante_evaluador(request, evento_id, participante_id):
    usuario = request.user
    evaluador = getattr(usuario, 'evaluador', None)
    if not evaluador or not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id, estado='admitido').exists():
        return HttpResponse("No tienes permiso para ver este participante.", status=403)
    participante = get_object_or_404(Participante, id=participante_id)
    inscripcion = InscripcionEvento.objects.filter(evento_id=evento_id, usuario=participante.usuario, estado='admitido').first()
    documentos = DocumentoParticipante.objects.filter(inscripcion__evento_id=evento_id, inscripcion__usuario=participante.usuario)
    return render(request, 'eventos/detalle_participante_evaluador.html', {
        'participante': participante,
        'inscripcion': inscripcion,
        'documentos': documentos,
        'evento_id': evento_id
    })


@login_required
def informacion_tecnica_evaluador(request, evento_id):
    usuario = request.user
    evaluador = getattr(usuario, 'evaluador', None)
    if not evaluador or not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id, estado='admitido').exists():
        return HttpResponse("No tienes permiso para cargar información técnica para este evento.", status=403)
    evento = Evento.objects.get(id=evento_id)
    if request.method == 'POST':
        form = InfoTecnicaEventoForm(request.POST, request.FILES)
        if form.is_valid():
            info = form.save(commit=False)
            info.evento = evento
            info.evaluador = evaluador
            info.save()
            messages.success(request, "Información técnica cargada correctamente.")
            return redirect('detalle_evento_evaluador', evento_id=evento_id)
    else:
        form = InfoTecnicaEventoForm()
    return render(request, 'eventos/informacion_tecnica_evaluador.html', {
        'form': form,
        'evento': evento
    })

@login_required
def ver_info_tecnica_evaluador(request, evento_id):
    evento = Evento.objects.get(id=evento_id)
    info_tecnica = InfoTecnicaEvento.objects.filter(evento=evento)
    return render(request, 'eventos/ver_info_tecnica_evaluador.html', {
        'evento': evento,
        'info_tecnica': info_tecnica
    })

@login_required
def subir_memoria_evento(request):
    from django.conf import settings
    import os
    mensaje = None
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        # Protección contra puertas traseras: solo permitir extensiones seguras
        EXTENSIONES_PERMITIDAS = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.txt', '.zip', '.rar']
        nombre_archivo = archivo.name.lower()
        _, extension = os.path.splitext(nombre_archivo)
        if extension not in EXTENSIONES_PERMITIDAS:
            mensaje = f"Extensión de archivo no permitida: {extension}"
        elif any(nombre_archivo.endswith(ext) for ext in ['.php', '.exe', '.sh', '.bat', '.py', '.js', '.asp', '.aspx', '.jsp', '.cgi']):
            mensaje = "Tipo de archivo potencialmente peligroso detectado."
        elif archivo.size > 20*1024*1024:  # Limitar tamaño a 20MB
            mensaje = "El archivo es demasiado grande (máx. 20MB)."
        else:
            ruta = os.path.join(settings.MEDIA_ROOT, 'info_tecnica_evento', archivo.name)
            with open(ruta, 'wb+') as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)
            mensaje = f"Archivo '{archivo.name}' subido correctamente."
    return render(request, 'eventos/subir_memoria_evento.html', {'mensaje': mensaje})


from django.templatetags.static import static

plantilla_path = static('images/plantilla.png')

import os
from django.http import HttpResponse
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

def descargar_imagen(request, evento_id):
    # Obtener datos del evento desde la base de datos
    evento = Evento.objects.get(id=evento_id)

    # Ruta de la plantilla
    plantilla_path = os.path.join(settings.BASE_DIR, 'eventos/static/images/plantilla.png')

    # Abrir la imagen
    imagen = Image.open(plantilla_path)

    # Crear un objeto para dibujar en la imagen
    draw = ImageDraw.Draw(imagen)

    # Ruta de las fuentes
    font_title_path = os.path.join(settings.BASE_DIR, 'eventos/static/fonts/Roboto-Bold.ttf')
    font_text_path = os.path.join(settings.BASE_DIR, 'eventos/static/fonts/Roboto-Regular.ttf')

    # Fuentes con tamaños diferentes
    font_title = ImageFont.truetype(font_title_path, size=80)  # Fuente más grande para el título
    font_text = ImageFont.truetype(font_text_path, size=30)    # Fuente más pequeña para el texto

    # Dibujar el título (nombre del evento) con ajuste de texto largo
    titulo = evento.nombre
    max_width_title = 1200  # Máximo ancho permitido para el título
    y_position_title = 300  # Posición inicial en el eje Y para el título
    for line in wrap_text(titulo, font_title, max_width_title):
        draw.text((50, y_position_title), line, fill="black", font=font_title)
        y_position_title += 90  # Incrementar la posición Y para la siguiente línea

    # Dibujar la descripción con ajuste de texto largo
    descripcion = evento.descripcion
    max_width = 1100  # Máximo ancho permitido para la descripción
    y_position = y_position_title + 50  # Posición inicial en el eje Y para la descripción
    for line in wrap_text(descripcion, font_text, max_width):
        draw.text((50, y_position), line, fill="black", font=font_text)
        y_position += 40  # Incrementar la posición Y para la siguiente línea

    # Dibujar la fecha y lugar con fuente más pequeña
    draw.text((240, 1290), f"Fecha: {evento.fecha_inicio} - {evento.fecha_fin}", fill="black", font=font_text)
    draw.text((240, 1380), f"Lugar: {evento.lugar}", fill="black", font=font_text)

    # Guardar la imagen en memoria
    response = HttpResponse(content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="Evento Eventsoft {evento.nombre}.png"'  # Configurar para descarga automática
    imagen.save(response, "PNG")
    return response

def wrap_text(text, font, max_width):
    """
    Divide el texto en líneas para que no exceda el ancho máximo.
    """
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        width, _ = font.getbbox(test_line)[2:]  # Usar getbbox para calcular el ancho del texto
        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

# ------------ SUPER ADMINISTRADOR ----------------
@login_required
def gestionar_items_instrumento_superadmin(request, evento_id, instrumento_id):
    instrumento = get_object_or_404(InstrumentoEvaluacion, id=instrumento_id, evento_id=evento_id)
    items = ItemInstrumento.objects.filter(instrumento=instrumento)

    if request.method == 'POST':
        form = ItemInstrumentoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.instrumento = instrumento  # Asignar el instrumento al ítem
            try:
                item.save()  # Esto ejecuta la validación en el modelo
                messages.success(request, "Ítem agregado correctamente.")
                return redirect('gestionar_items_instrumento', evento_id=evento_id, instrumento_id=instrumento_id)
            except ValidationError as e:
                # Agregar el error al formulario para mostrarlo en el HTML
                form.add_error(None, e.message)
        else:
            messages.error(request, "Hay errores en el formulario. Por favor, corrígelos.")
    else:
        form = ItemInstrumentoForm()

    return render(request, 'eventos/gestionar_items_instrumento_superadmin.html', {
        'instrumento': instrumento,
        'items': items,
        'form': form,
        'evento_id': evento_id,
    })

@login_required
def superadmin_crear_instrumento(request, evento_id):
    from django.contrib import messages
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_roles')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = InstrumentoEvaluacionForm(request.POST, request.FILES)
        if form.is_valid():
            instrumento = form.save(commit=False)
            instrumento.evento = evento
            instrumento.save()
            messages.success(request, "Instrumento creado correctamente.")
            return redirect('eventos_gestion_instrumentos_admin')
    else:
        form = InstrumentoEvaluacionForm()
    return render(request, 'eventos/superadmin_crear_instrumento.html', {'form': form, 'evento': evento})

@login_required
def superadmin_tabla_posiciones(request, evento_id):
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        from django.contrib import messages
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_roles')
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante
    from evaluaciones.models import CalificacionParticipante
    from django.db.models import Sum
    evento = get_object_or_404(Evento, id=evento_id)
    inscripciones = InscripcionEvento.objects.filter(evento=evento, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    ranking = []
    for participante in participantes:
        puntaje_total = CalificacionParticipante.objects.filter(
            evento=evento,
            participante=participante
        ).aggregate(total=Sum('puntaje'))['total'] or 0
        ranking.append({
            'participante': participante,
            'puntaje_total': puntaje_total
        })
    ranking = sorted(ranking, key=lambda x: x['puntaje_total'], reverse=True)
    # Descarga CSV
    if request.GET.get('descargar') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=tabla_posiciones_{evento.nombre}.csv'
        writer = csv.writer(response)
        writer.writerow(['Posición', 'Nombre', 'Email', 'Puntaje total'])
        for idx, item in enumerate(ranking, 1):
            writer.writerow([
                idx,
                f"{item['participante'].usuario.first_name} {item['participante'].usuario.last_name}",
                item['participante'].usuario.email,
                item['puntaje_total']
            ])
        return response
    return render(request, 'eventos/superadmin_tabla_posiciones.html', {
        'evento': evento,
        'ranking': ranking
    })

@login_required
def superadmin_detalle_calificaciones_participante(request, evento_id, participante_id):
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_roles')
    evento = get_object_or_404(Evento, id=evento_id)
    participante = get_object_or_404(Participante, id=participante_id)
    instrumentos = evento.instrumentos.all()
    from evaluaciones.models import CalificacionParticipante
    from usuarios.models import Evaluador
    detalle = []
    for instrumento in instrumentos:
        items = instrumento.items.all()
        for item in items:
            calificaciones = CalificacionParticipante.objects.filter(
                evento=evento,
                instrumento=instrumento,
                item=item,
                participante=participante
            )
            for calificacion in calificaciones:
                detalle.append({
                    'instrumento': instrumento,
                    'item': item,
                    'evaluador': calificacion.evaluador,
                    'puntaje': calificacion.puntaje
                })
    # Agrupar por instrumento e ítem para mostrar en el template
    from collections import defaultdict
    agrupado = defaultdict(lambda: defaultdict(list))
    for d in detalle:
        agrupado[d['instrumento']][d['item']].append({
            'evaluador': d['evaluador'],
            'puntaje': d['puntaje']
        })
    return render(request, 'eventos/superadmin_detalle_calificaciones_participante.html', {
        'evento': evento,
        'participante': participante,
        'agrupado': agrupado
    })

@login_required
def gestionar_items_instrumento_superadmin(request, evento_id, instrumento_id):
    evaluador = getattr(request.user, 'evaluador', None)
    # Verificar que el evaluador esté asignado a este evento
    instrumento = get_object_or_404(InstrumentoEvaluacion, id=instrumento_id, evento_id=evento_id)
    items = ItemInstrumento.objects.filter(instrumento=instrumento)
    # Obtener participantes admitidos del evento
    from inscripciones.models import InscripcionEvento
    from usuarios.models import Participante
    inscripciones = InscripcionEvento.objects.filter(evento_id=evento_id, estado='admitido')
    participantes = Participante.objects.filter(usuario__in=[i.usuario for i in inscripciones])
    if request.method == 'POST':
        form = ItemInstrumentoForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.instrumento = instrumento
            item.save()
            return redirect('gestionar_items_instrumento_superadmin', evento_id=evento_id, instrumento_id=instrumento_id)
    else:
        form = ItemInstrumentoForm()
    return render(request, 'eventos/gestionar_items_instrumento_superadmin.html', {
        'instrumento': instrumento,
        'items': items,
        'form': form,
        'evento_id': evento_id,
        'participantes': participantes
    })

@login_required
def editar_item_instrumento_superadmin(request, evento_id, instrumento_id, item_id):
    evaluador = getattr(request.user, 'evaluador', None)
    item = get_object_or_404(ItemInstrumento, id=item_id, instrumento_id=instrumento_id)
    if request.method == 'POST':
        form = ItemInstrumentoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('gestionar_items_instrumento', evento_id=evento_id, instrumento_id=instrumento_id)
    else:
        form = ItemInstrumentoForm(instance=item)
    return render(request, 'eventos/editar_item_instrumento_superadmin.html', {'form': form, 'item': item, 'instrumento_id': instrumento_id, 'evento_id': evento_id})

@login_required
def eliminar_item_instrumento_superadmin(request, evento_id, instrumento_id, item_id):
    evaluador = getattr(request.user, 'evaluador', None)
    item = get_object_or_404(ItemInstrumento, id=item_id, instrumento_id=instrumento_id)
    if request.method == 'POST':
        item.delete()
        return redirect('gestionar_items_instrumento_superadmin', evento_id=evento_id, instrumento_id=instrumento_id)
    return render(request, 'eventos/eliminar_item_instrumento_superadmin.html', {'item': item, 'instrumento_id': instrumento_id, 'evento_id': evento_id})

@login_required
def subir_memoria_evento(request):
    from django.conf import settings
    import os
    mensaje = None
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        # Protección contra puertas traseras: solo permitir extensiones seguras
        EXTENSIONES_PERMITIDAS = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.jpg', '.jpeg', '.png', '.txt', '.zip', '.rar']
        nombre_archivo = archivo.name.lower()
        _, extension = os.path.splitext(nombre_archivo)
        if extension not in EXTENSIONES_PERMITIDAS:
            mensaje = f"Extensión de archivo no permitida: {extension}"
        elif any(nombre_archivo.endswith(ext) for ext in ['.php', '.exe', '.sh', '.bat', '.py', '.js', '.asp', '.aspx', '.jsp', '.cgi']):
            mensaje = "Tipo de archivo potencialmente peligroso detectado."
        elif archivo.size > 20*1024*1024:  # Limitar tamaño a 20MB
            mensaje = "El archivo es demasiado grande (máx. 20MB)."
        else:
            ruta = os.path.join(settings.MEDIA_ROOT, 'info_tecnica_evento', archivo.name)
            with open(ruta, 'wb+') as destino:
                for chunk in archivo.chunks():
                    destino.write(chunk)
            mensaje = f"Archivo '{archivo.name}' subido correctamente."
    return render(request, 'eventos/subir_memoria_evento_superadmin.html', {'mensaje': mensaje})

@login_required
def editar_evento_superadmin(request, evento_id):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para editar eventos.")
        return redirect('inicio_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento editado exitosamente.")
            return redirect('inicio_superadmin')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'eventos/editar_evento_superadmin.html', {'form': form, 'evento': evento})

@login_required
def participantes_preinscritos_superadmin(request, evento_id):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    inscripciones = InscripcionEvento.objects.filter(evento_id=evento_id, usuario__rol='participante')
    datos = []
    for inscripcion in inscripciones:
        documentos = DocumentoParticipante.objects.filter(inscripcion=inscripcion)
        datos.append({'inscripcion': inscripcion, 'documentos': documentos})
    return render(request, 'usuarios/participantes_preinscritos_superadmin.html', {'datos': datos})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Evento

@login_required
def eventos_lista_superadmin(request):
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        return redirect('inicio_roles')
    eventos = Evento.objects.all().order_by('-fecha_inicio')
    return render(request, 'eventos/eventos_lista_superadmin.html', {'eventos': eventos})

@login_required
def aprobar_evento(request, evento_id):
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        return redirect('inicio_roles')
    evento = get_object_or_404(Evento, id=evento_id)
    evento.estado = 'aceptado'
    evento.save()
    return redirect('eventos_lista_superadmin')


# Vista para rechazar evento (superadmin)
from django.views.decorators.http import require_POST

@login_required
@require_POST
def rechazar_evento(request, evento_id):
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        return redirect('inicio_roles')
    evento = get_object_or_404(Evento, id=evento_id)
    evento.estado = 'rechazado'
    evento.save()
    return redirect('eventos_lista_superadmin')