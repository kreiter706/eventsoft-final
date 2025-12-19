# Vista para gestionar todos los administradores de evento (superadmin)
from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser or u.rol == 'superadmin')
def gestionar_admins(request):
    admins = Usuario.objects.filter(rol='admin')
    return render(request, 'usuarios/superadmin/gestionar_admins.html', {'admins': admins})
from .forms_cambiar_estado_codigo import CambiarEstadoCodigoForm
# Vista para cambiar el estado del código de acceso de un admin
from django.contrib.auth.decorators import user_passes_test
@user_passes_test(lambda u: u.is_superuser or u.rol == 'superadmin')
def cambiar_estado_codigo_acceso(request, usuario_id):
    from .models_codigo_acceso import EventAdminAccessCode
    usuario = get_object_or_404(Usuario, id=usuario_id)
    try:
        codigo = usuario.event_access_code
    except EventAdminAccessCode.DoesNotExist:
        messages.error(request, 'Este usuario no tiene código de acceso.')
        return redirect('listar_usuarios')
    if request.method == 'POST':
        form = CambiarEstadoCodigoForm(request.POST, instance=codigo)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El estado del código fue actualizado exitosamente!')
            return redirect('gestionar_admins')
    else:
        form = CambiarEstadoCodigoForm(instance=codigo)
    return render(request, 'usuarios/cambiar_estado_codigo_acceso.html', {'form': form, 'usuario': usuario})
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pytz
from django.shortcuts import render, get_object_or_404, redirect

@login_required
def enviar_correo_masivo_evento(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    # Participantes
    insc_part = InscripcionEvento.objects.filter(evento=evento, usuario__rol='participante')
    usuarios_part = [insc.usuario for insc in insc_part]
    # Asistentes
    insc_asist = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente')
    usuarios_asist = [insc.usuario for insc in insc_asist]
    # Evaluadores
    from eventos.models import EvaluadorEvento
    rels_eval = EvaluadorEvento.objects.filter(evento=evento)
    usuarios_eval = [rel.evaluador.usuario for rel in rels_eval]
    usuarios = list(set(usuarios_part + usuarios_asist + usuarios_eval))
    enviados = False
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        emails = [u.email for u in usuarios if u.email]
        if emails and asunto and mensaje:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                emails,
                fail_silently=False
            )
            enviados = True
            messages.success(request, f"Correos enviados a {len(emails)} usuarios del evento.")
        else:
            messages.error(request, "Faltan datos o no hay destinatarios.")
    return render(request, 'usuarios/seleccionar_rol_envio_correo.html', {
        'evento': evento,
        'roles': [
            ('participante', 'Participantes'),
            ('evaluador', 'Evaluadores'),
            ('asistente', 'Asistentes'),
        ],
        'enviados': enviados
    })
from eventos.forms import PresentacionEventoForm
from eventos.models import PresentacionEvento
# ----------- Subir presentaciones PDF -----------

from django.contrib.auth.decorators import login_required
@login_required
def subir_presentacion_evento(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para subir presentaciones.")
        return redirect('/usuarios/login/')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = PresentacionEventoForm(request.POST, request.FILES)
        if form.is_valid():
            presentacion = form.save(commit=False)
            presentacion.evento = evento
            presentacion.save()
            messages.success(request, "Presentación subida exitosamente.")
            return redirect('subir_presentacion_evento', evento_id=evento.id)
    else:
        form = PresentacionEventoForm()
    return render(request, 'usuarios/subir_presentacion_evento.html', {'form': form, 'evento': evento})
from eventos.models import Evento

from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def lista_eventos_configurar_certificados(request):
    if not hasattr(request.user, 'rol') or request.user.rol != 'admin':
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        eventos = Evento.objects.filter(creador=request.user).order_by('-fecha_inicio')
    else:
        eventos = Evento.objects.all().order_by('-fecha_inicio')
    return render(request, 'usuarios/lista_eventos_configurar_certificados.html', {'eventos': eventos})
# ...existing code...
from django.shortcuts import render, get_object_or_404, redirect
from eventos.forms import ConfiguracionCertificadoEventoForm
from eventos.models import ConfiguracionCertificadoEvento, Evento

def configurar_certificados_evento(request, evento_id):
    if not request.user.is_authenticated or getattr(request.user, 'rol', None) != 'admin':
        from django.http import HttpResponse
        return HttpResponse('No tienes permisos para configurar certificados.', status=403)
    evento = get_object_or_404(Evento, id=evento_id)
    try:
        config = evento.configuracion_certificado
    except ConfiguracionCertificadoEvento.DoesNotExist:
        config = None

    if request.method == 'POST':
        form = ConfiguracionCertificadoEventoForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.evento = evento
            config.save()
            return render(request, 'usuarios/configurar_certificados_evento.html', {
                'form': form,
                'evento_id': evento_id,
                'guardado': True
            })
    else:
        form = ConfiguracionCertificadoEventoForm(instance=config)

    return render(request, 'usuarios/configurar_certificados_evento.html', {
        'form': form,
        'evento_id': evento_id
    })
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CrearUsuarioForm, ProgramacionEventoForm
from eventos.models import InfoTecnicaEvento
from eventos.models import EvaluadorEvento
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from eventos.forms import PreinscripcionParticipanteForm
from .models import Usuario, Participante, Evaluador, Asistente, AdministradorEvento
from inscripciones.models import InscripcionEvento
from documentos.models import DocumentoParticipante
from eventos.models import Evento
from proyectos.models import Proyecto
from inscripciones.models import InscripcionEvento
from documentos.models import DocumentoParticipante
from eventos.forms import PreinscripcionEvaluadorForm
from django.contrib.auth.decorators import login_required
from evaluaciones.models import Evaluacion
import secrets
from PIL import Image
from io import BytesIO
import qrcode
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django import forms
from django import forms

    
# ----------- Vistas de autenticación y perfiles -----------



class CustomLoginView(LoginView):
    from .custom_auth_form import CustomAuthenticationForm
    form_class = CustomAuthenticationForm

    def get_success_url(self):
        from django.urls import reverse
        from django.utils import timezone
        from django.contrib.auth import logout
        user = self.request.user
        # Solo para admin, no para superadmin
        if user.rol == 'admin':
            access_code = getattr(user, 'event_access_code', None)
            if access_code:
                # Verificar estado del código
                if access_code.estado == 'suspendido':
                    from django.contrib import messages
                    messages.error(self.request, 'No puedes ingresar: tu código de acceso fue suspendido. Contacta al superadministrador.')
                    logout(self.request)
                    return reverse('login')
                elif access_code.estado == 'cancelado':
                    from django.contrib import messages
                    messages.error(self.request, 'No puedes ingresar: tu código de acceso fue cancelado. Contacta al superadministrador.')
                    logout(self.request)
                    return reverse('login')
                # Verificar expiración
                if access_code.expires_at:
                    bogota_tz = pytz.timezone('America/Bogota')
                    now_bogota = timezone.now().astimezone(bogota_tz)
                    expires_at_bogota = access_code.expires_at.astimezone(bogota_tz)
                    if now_bogota > expires_at_bogota:
                        from django.contrib import messages
                        messages.error(self.request, 'No puedes ingresar a tu perfil de admin porque tu acceso ha expirado. Si crees que es un error, contacta al superadministrador.')
                        logout(self.request)
                        return reverse('login')
            return reverse('inicio_admin')
        elif user.rol == 'superadmin':
            return reverse('inicio_superadmin')
        elif user.rol == 'participante':
            return reverse('mis_inscripciones')
        elif user.rol == 'evaluador':
            return reverse('inicio_evaluador')
        elif user.rol == 'asistente':
            return reverse('inicio_asistente')
        return super().get_success_url()

    def form_valid(self, form):
        """Log useful info when login succeeds to help debug post-login logic."""
        try:
            user = form.get_user()
        except Exception:
            user = None
        import logging
        logger = logging.getLogger('django')
        logger.debug(f"Login form_valid called. user={getattr(user, 'email', None)} rol={getattr(user, 'rol', None)} is_active={getattr(user, 'is_active', None)}")
        # If admin, also log access code state if present
        if user and getattr(user, 'rol', None) == 'admin':
            try:
                access_code = getattr(user, 'event_access_code', None)
                logger.debug(f"Admin access_code: {access_code and getattr(access_code, 'estado', None)} expires_at={access_code and getattr(access_code, 'expires_at', None)}")
            except Exception as e:
                logger.debug(f"Error checking access_code: {e}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Log failed login attempts to help debugging."""
        import logging
        logger = logging.getLogger('django')
        try:
            data = self.request.POST.dict()
        except Exception:
            data = {}
        logger.debug(f"Login form_invalid called. POST={data} errors={form.errors}")
        return super().form_invalid(form)


@csrf_exempt
def auth_check(request):
    """Endpoint de diagnóstico (solo DEBUG y localhost).
    POST params: username or email, password
    Devuelve JSON con: exists, is_active, has_usable_password, check_password, perfiles y estados.
    """
    from django.conf import settings
    # Solo activo en DEBUG y desde localhost
    if not getattr(settings, 'DEBUG', False):
        return JsonResponse({'error': 'Not available'}, status=404)
    # Revisar origen (soporte básico)
    host = request.META.get('REMOTE_ADDR') or request.META.get('REMOTE_HOST')
    if host not in (None, '127.0.0.1', '::1', 'localhost') and not request.META.get('HTTP_HOST', '').startswith('127.0.0.1'):
        return JsonResponse({'error': 'Forbidden'}, status=403)

    # Support GET for quick debugging and POST for form-style calls
    username = (request.POST.get('username') or request.POST.get('email') or
                request.GET.get('username') or request.GET.get('email') or '')
    password = (request.POST.get('password') or request.GET.get('password') or '')
    if not username:
        return JsonResponse({'error': 'username/email required'}, status=400)

    # Intentar localizar usuario
    from .models import Usuario
    user = Usuario.objects.filter(email__iexact=username).first() or Usuario.objects.filter(username__iexact=username).first()
    if not user:
        return JsonResponse({'exists': False})

    perfiles = {}
    for rel in ('participante', 'evaluador', 'asistente', 'admin_evento'):
        try:
            obj = getattr(user, rel)
            perfiles[rel] = getattr(obj, 'estado', None)
        except Exception:
            perfiles[rel] = None

    result = {
        'exists': True,
        'email': user.email,
        'username': user.username,
        'is_active': user.is_active,
        'has_usable_password': user.has_usable_password(),
        'check_password': user.check_password(password) if password else None,
        'rol': user.rol,
        'perfiles': perfiles,
    }
    return JsonResponse(result)

@login_required
def perfil_participante(request):
    usuario = request.user
    if usuario.rol != 'participante':
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    documentos = DocumentoParticipante.objects.filter(inscripcion__usuario=usuario)
    return render(request, 'usuarios/perfil_participante.html', {'usuario': usuario, 'documentos': documentos})

@login_required
def perfil_asistente(request):
    usuario = request.user
    if usuario.rol != 'asistente':
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    from inscripciones.models import InscripcionEvento
    inscripciones = InscripcionEvento.objects.filter(usuario=usuario)
    return render(request, 'usuarios/perfil_asistente.html', {'usuario': usuario, 'inscripciones': inscripciones})

# ----------- Vistas de usuario -----------

from django.contrib import messages
from django.contrib.auth.decorators import login_required

def editar_cuenta_asistente(request):
    user = request.user
    if user.rol != 'asistente':
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cambios = False
        if nombre and nombre != user.first_name:
            user.first_name = nombre
            cambios = True
        if email and email != user.email:
            user.email = email
            cambios = True
        # Solo permitir cambio de contraseña si NO es admin de evento
        if password and not hasattr(user, 'admin_evento'):
            user.set_password(password)
            cambios = True
        if cambios:
            user.save()
            messages.success(request, 'Datos actualizados correctamente.')
            # Si cambió la contraseña, es recomendable volver a iniciar sesión
            from django.contrib.auth import update_session_auth_hash
            if password:
                update_session_auth_hash(request, user)
        return redirect('perfil_asistente')
    return render(request, 'usuarios/editar_cuenta_asistente.html', {'user': user})
@login_required
def editar_cuenta_asistente(request):
    user = request.user
    if user.rol != 'asistente':
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cambios = False
        if nombre and nombre != user.first_name:
            user.first_name = nombre
            cambios = True
        if email and email != user.email:
            user.email = email
            cambios = True
        # Solo permitir cambio de contraseña si NO es admin de evento
        if password and not hasattr(user, 'admin_evento'):
            user.set_password(password)
            cambios = True
        if cambios:
            user.save()
            messages.success(request, 'Datos actualizados correctamente.')
            from django.contrib.auth import update_session_auth_hash
            if password and not hasattr(user, 'admin_evento'):
                update_session_auth_hash(request, user)
        return redirect('perfil_asistente')
    return render(request, 'usuarios/editar_cuenta_asistente.html', {'user': user})

def crear_usuario(request):
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Solo permitir set_password si no es admin_evento
            if form.cleaned_data['rol'] != 'admin':
                # Solo permitir set_password si no es admin_evento
                if form.cleaned_data['rol'] != 'admin':
                    user.set_password(form.cleaned_data['password'])
            user.save()
            rol = form.cleaned_data['rol']
            if rol == 'participante':
                Participante.objects.create(usuario=user)
            elif rol == 'evaluador':
                Evaluador.objects.create(usuario=user)
            elif rol == 'asistente':
                Asistente.objects.create(usuario=user)
            elif rol == 'admin_evento':
                AdministradorEvento.objects.create(usuario=user)
            return redirect('listar_usuarios')
    else:
        form = CrearUsuarioForm()
    return render(request, 'usuarios/crear_usuario.html', {'form': form})

def listar_usuarios(request):
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        # Solo mostrar usuarios inscritos en eventos creados por este admin
        from inscripciones.models import InscripcionEvento
        eventos_admin = Evento.objects.filter(creador=request.user, estado='aceptado')
        usuarios_ids = InscripcionEvento.objects.filter(evento__in=eventos_admin).values_list('usuario_id', flat=True).distinct()
        usuarios = Usuario.objects.filter(id__in=usuarios_ids)
    else:
        usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar_usuarios.html', {'usuarios': usuarios})

def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('listar_usuarios')
    else:
        form = CrearUsuarioForm(instance=usuario)
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'usuario': usuario})

# ----------- Vistas de inscripciones (participante y asistente) -----------
@login_required
def mis_inscripciones(request):
    usuario = request.user
    inscripciones = InscripcionEvento.objects.filter(usuario=usuario)
    return render(request, 'usuarios/mis_inscripciones.html', {'inscripciones': inscripciones})

@login_required
def crear_inscripcion_participante(request, evento_id):
    usuario = request.user
    evento = get_object_or_404(Evento, id=evento_id)
    usuario.rol = 'participante'
    usuario.save()
    inscripcion, created = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
    return redirect('editar_preinscripcion_participante', evento_id=evento.id, usuario_id=usuario.id)

@login_required
def editar_preinscripcion_participante(request, evento_id, usuario_id):
    evento = get_object_or_404(Evento, id=evento_id)
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.user.rol != 'participante' or request.user.id != usuario.id:
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    inscripcion = get_object_or_404(InscripcionEvento, usuario=usuario, evento=evento)
    documento_participante = DocumentoParticipante.objects.filter(inscripcion=inscripcion).first()
    if request.method == 'POST':
        form = PreinscripcionParticipanteForm(request.POST, request.FILES)
        if form.is_valid():
            usuario.first_name = form.cleaned_data['nombre']
            usuario.email = form.cleaned_data['correo']
            usuario.rol = 'participante'
            # Generar siempre una nueva clave de acceso
            import secrets
            clave_generada = secrets.token_urlsafe(8)
            # Guardar la clave en InscripcionEvento
            inscripcion.clave_acceso = clave_generada
            inscripcion.save()
            # Solo permitir set_password si no es admin_evento
            if not hasattr(usuario, 'admin_evento'):
                usuario.set_password(clave_generada)
            usuario.save()
            if documento_participante:
                documento_participante.archivo = form.cleaned_data['documento']
                documento_participante.save()
            else:
                DocumentoParticipante.objects.create(
                    inscripcion=inscripcion,
                    archivo=form.cleaned_data['documento'],
                    descripcion="Documento de preinscripción"
                )
            mensaje = f"¡Preinscripción exitosa!\nEvento: {evento.nombre}\n\nTu clave de acceso es: {clave_generada}\n\nGuárdala en un lugar seguro."
            return render(request, 'usuarios/preinscripcion_exitosa.html', {'evento': evento, 'mensaje': mensaje})
    else:
        form = PreinscripcionParticipanteForm(initial={
            'nombre': usuario.first_name,
            'correo': usuario.email,
        })
    return render(request, 'usuarios/editar_preinscripcion.html', {'form': form, 'evento': evento})

@login_required
def crear_inscripcion_asistente(request, evento_id):
    usuario = request.user
    evento = get_object_or_404(Evento, id=evento_id)
    usuario.rol = 'asistente'
    usuario.save()
    inscripcion, created = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
    return redirect('editar_preinscripcion_asistente', evento_id=evento.id, usuario_id=usuario.id)

@login_required
def editar_preinscripcion_asistente(request, evento_id, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    if request.user.rol != 'asistente' or request.user.id != usuario.id:
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    evento = get_object_or_404(Evento, id=evento_id)
    inscripcion = get_object_or_404(InscripcionEvento, usuario=usuario, evento=evento)
    if request.method == 'POST':
        return render(request, 'usuarios/preinscripcion_exitosa.html', {'evento': evento, 'mensaje': '¡Preinscripción modificada exitosamente!'})
    return render(request, 'usuarios/editar_preinscripcion_asistente.html', {'evento': evento, 'usuario': usuario})

@login_required
def cancelar_preinscripcion(request, evento_id, usuario_id):
    if request.user.rol != 'participante' or request.user.id != int(usuario_id):
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    inscripcion = InscripcionEvento.objects.filter(evento_id=evento_id, usuario_id=usuario_id).first()
    if inscripcion:
        inscripcion.delete()
        messages.success(request, "Preinscripción cancelada exitosamente.")
    else:
        messages.error(request, "No se encontró la preinscripción.")
    return redirect('mis_inscripciones')

@login_required
def cancelar_preinscripcion_asistente(request, evento_id, usuario_id):
    if request.user.rol != 'asistente' or request.user.id != int(usuario_id):
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    inscripcion = InscripcionEvento.objects.filter(evento_id=evento_id, usuario_id=usuario_id).first()
    if inscripcion:
        inscripcion.delete()
        messages.success(request, "Preinscripción cancelada exitosamente.")
    else:
        messages.error(request, "No se encontró la preinscripción.")
    return redirect('mis_inscripciones')

# ----------- Vistas de descarga de comprobantes -----------

@login_required
def previsualizar_certificado_evento(request, evento_id):
    from eventos.models import Evento, ConfiguracionCertificadoEvento
    evento = get_object_or_404(Evento, id=evento_id)
    try:
        config = evento.configuracion_certificado
    except ConfiguracionCertificadoEvento.DoesNotExist:
        config = None
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 800, "Certificado de Ejemplo")
    p.setFont("Helvetica", 12)
    nombre_evento = config.nombre_evento if config and config.nombre_evento else evento.nombre
    fecha_inicio = config.fecha_inicio_evento if config and config.fecha_inicio_evento else evento.fecha_inicio
    fecha_fin = config.fecha_fin_evento if config and config.fecha_fin_evento else evento.fecha_fin
    lugar = config.lugar_evento if config and config.lugar_evento else evento.lugar
    organizador = config.organizador_evento if config and config.organizador_evento else "Organización del evento"
    mensaje = config.mensaje_certificado if config and config.mensaje_certificado else ""
    p.drawString(100, 770, f"Evento: {nombre_evento}")
    p.drawString(100, 750, f"Fecha de inicio: {fecha_inicio}")
    p.drawString(100, 730, f"Fecha de finalización: {fecha_fin}")
    p.drawString(100, 710, f"Lugar: {lugar}")
    p.drawString(100, 690, f"Organizador: {organizador}")
    p.drawString(100, 670, f"Nombre ejemplo: Juan Pérez (juan@example.com)")
    if mensaje:
        p.setFont("Helvetica-Oblique", 12)
        p.drawString(100, 650, mensaje)
        p.setFont("Helvetica", 12)
    qr_data = f"Evento: {nombre_evento} | Nombre: Juan Pérez | Email: juan@example.com | Previsualización"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_pil = Image.open(qr_buffer)
    p.drawInlineImage(qr_pil, 100, 550, 100, 100)
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
def descargar_certificado_participante(request, inscripcion_id):
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id, usuario=request.user)
    if request.user.rol != 'participante':
        return HttpResponse("No tienes permiso para descargar el certificado.", status=403)
    if inscripcion.estado != 'admitido':
        return HttpResponse("No tienes permiso para descargar el certificado.", status=403)
    # Obtener configuración personalizada del certificado
    try:
        config = inscripcion.evento.configuracion_certificado
    except Exception:
        config = None
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 800, "Certificado de Participación")
    p.setFont("Helvetica", 12)
    nombre_evento = config.nombre_evento if config and config.nombre_evento else inscripcion.evento.nombre
    fecha_inicio = config.fecha_inicio_evento if config and config.fecha_inicio_evento else inscripcion.evento.fecha_inicio
    fecha_fin = config.fecha_fin_evento if config and config.fecha_fin_evento else inscripcion.evento.fecha_fin
    lugar = config.lugar_evento if config and config.lugar_evento else inscripcion.evento.lugar
    organizador = config.organizador_evento if config and config.organizador_evento else "Organización del evento"
    mensaje = config.mensaje_certificado if config and config.mensaje_certificado else ""
    p.drawString(100, 770, f"Evento: {nombre_evento}")
    p.drawString(100, 750, f"Fecha de inicio: {fecha_inicio}")
    p.drawString(100, 730, f"Fecha de finalización: {fecha_fin}")
    p.drawString(100, 710, f"Lugar: {lugar}")
    p.drawString(100, 690, f"Organizador: {organizador}")
    p.drawString(100, 670, f"Participante: {inscripcion.usuario.first_name} {inscripcion.usuario.last_name} ({inscripcion.usuario.email})")
    if mensaje:
        p.setFont("Helvetica-Oblique", 12)
        p.drawString(100, 650, mensaje)
        p.setFont("Helvetica", 12)
    qr_data = f"Evento: {nombre_evento} | Participante: {inscripcion.usuario.first_name} {inscripcion.usuario.last_name} | Email: {inscripcion.usuario.email} | Estado: {inscripcion.estado}"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_pil = Image.open(qr_buffer)
    p.drawInlineImage(qr_pil, 100, 550, 100, 100)
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
def descargar_certificado_asistente(request, inscripcion_id):
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id, usuario=request.user)
    if inscripcion.estado != 'admitido':
        return HttpResponse("No tienes permiso para descargar el certificado.", status=403)
    # Obtener configuración personalizada del certificado
    try:
        config = inscripcion.evento.configuracion_certificado
    except ConfiguracionCertificadoEvento.DoesNotExist:
        config = None
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 800, "Certificado de Asistencia")
    p.setFont("Helvetica", 12)
    nombre_evento = config.nombre_evento if config and config.nombre_evento else inscripcion.evento.nombre
    fecha_inicio = config.fecha_inicio_evento if config and config.fecha_inicio_evento else inscripcion.evento.fecha_inicio
    fecha_fin = config.fecha_fin_evento if config and config.fecha_fin_evento else inscripcion.evento.fecha_fin
    lugar = config.lugar_evento if config and config.lugar_evento else inscripcion.evento.lugar
    organizador = config.organizador_evento if config and config.organizador_evento else "Organización del evento"
    mensaje = config.mensaje_certificado if config and config.mensaje_certificado else ""
    p.drawString(100, 770, f"Evento: {nombre_evento}")
    p.drawString(100, 750, f"Fecha de inicio: {fecha_inicio}")
    p.drawString(100, 730, f"Fecha de finalización: {fecha_fin}")
    p.drawString(100, 710, f"Lugar: {lugar}")
    p.drawString(100, 690, f"Organizador: {organizador}")
    p.drawString(100, 670, f"Asistente: {inscripcion.usuario.first_name} {inscripcion.usuario.last_name} ({inscripcion.usuario.email})")
    if mensaje:
        p.setFont("Helvetica-Oblique", 12)
        p.drawString(100, 650, mensaje)
        p.setFont("Helvetica", 12)
    qr_data = f"Evento: {nombre_evento} | Asistente: {inscripcion.usuario.first_name} {inscripcion.usuario.last_name} | Email: {inscripcion.usuario.email} | Estado: {inscripcion.estado}"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_pil = Image.open(qr_buffer)
    p.drawInlineImage(qr_pil, 100, 550, 100, 100)
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
def descargar_comprobante(request, inscripcion_id):
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id, usuario=request.user)
    data = f"Inscripción: {inscripcion.id} - Evento: {inscripcion.evento.nombre} - Usuario: {inscripcion.usuario.email}"
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')

@login_required
def descargar_comprobante_asistente(request, inscripcion_id):
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id, usuario=request.user)
    if request.user.rol != 'asistente':
        return HttpResponse("No tienes permiso para descargar el comprobante.", status=403)
    if inscripcion.estado != 'admitido':
        return HttpResponse("No tienes permiso para descargar el comprobante.", status=403)
    # Generar comprobante PDF con diseño mejorado
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    import os
    buffer = BytesIO()
    width, height = letter
    p = canvas.Canvas(buffer, pagesize=letter)

    # Rutas a imágenes estáticas (fondo y logo)
    try:
        bg_path = os.path.join(settings.BASE_DIR, 'static', 'fondos', 'fondo_comprobante.png')
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'fondos', 'logosena.png')
    except Exception:
        bg_path = None
        logo_path = None

    # Dibujar fondo suave si existe
    if bg_path and os.path.exists(bg_path):
        try:
            p.drawImage(bg_path, 0, 0, width=width, height=height, mask='auto')
        except Exception:
            pass

    # Encabezado: banda superior con título centrado y logo superpuesto sobre la línea
    banner_h = 84
    banner_y = height - banner_h
    try:
        # banda superior
        p.setFillColorRGB(0.01, 0.47, 0.39)  # verde oscuro
        p.roundRect(36, banner_y, width-72, banner_h, 6, stroke=0, fill=1)
        # título en blanco centrado
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(width/2, banner_y + banner_h/2 + 6, "Comprobante de inscripción")
    except Exception:
        # fallback simple
        p.setFillColorRGB(0.02, 0.45, 0.36)
        p.setFont("Helvetica-Bold", 22)
        p.drawCentredString(width/2, height-60, "Comprobante de inscripción")

    # Línea separadora justo debajo de la banda (con sombra ligera)
    sep_y = banner_y - 6
    p.setStrokeColorRGB(0.9, 0.9, 0.9)
    p.setLineWidth(1.5)
    p.line(48, sep_y, width-48, sep_y)

    # Logo superpuesto sobre la línea (centrado a la izquierda)
    if logo_path and os.path.exists(logo_path):
        try:
            logo_w = 80
            logo_h = 80
            logo_x = 60
            # dibujar rectángulo blanco detrás del logo para resaltarlo
            p.setFillColorRGB(1,1,1)
            p.roundRect(logo_x-8, sep_y-8, logo_w+16, logo_h+16, 10, stroke=0, fill=1)
            p.drawImage(logo_path, logo_x, sep_y-8, width=logo_w, height=logo_h, mask='auto')
        except Exception:
            pass
    else:
        # Dibujar logo simple (círculo estilizado + texto) como fallback vectorial
        try:
            logo_w = 80
            logo_h = 80
            logo_x = 60
            p.setFillColorRGB(1,1,1)
            p.roundRect(logo_x-8, sep_y-8, logo_w+16, logo_h+16, 10, stroke=0, fill=1)
            # Triángulo estilizado
            p.setFillColorRGB(0.02, 0.45, 0.36)
            p.polygon([logo_x+8, sep_y+logo_h-12, logo_x+logo_w/2, sep_y+12, logo_x+logo_w-8, sep_y+logo_h-12], stroke=0, fill=1)
            p.setFillColorRGB(0,0,0)
            p.setFont("Helvetica-Bold", 10)
            p.drawCentredString(logo_x+logo_w/2, sep_y-6, "SENA")
        except Exception:
            pass

    # Caja blanca para contenido
    box_x = 48
    box_y = height-460
    box_w = width - 96
    box_h = 340
    p.setFillColorRGB(1, 1, 1)
    p.roundRect(box_x, box_y, box_w, box_h, 12, stroke=0, fill=1)

    # Preparar área de texto y QR
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfbase.pdfmetrics import stringWidth
    text_x = box_x + 28
    qr_size = 170
    value_x = box_x + box_w - qr_size - 34
    text_area_width = value_x - text_x - 20
    cur_y = box_y + box_h - 28
    p.setFillColorRGB(0.12, 0.12, 0.12)

    # Helper para dibujar etiqueta + valor con wrapping
    def draw_label_value(label, value, y, label_font="Helvetica", label_size=11, value_font="Helvetica-Bold", value_size=11):
        # etiqueta
        p.setFont(label_font, label_size)
        p.drawString(text_x, y, label)
        # valor con wrap
        wrapped = simpleSplit(str(value), value_font, value_size, text_area_width)
        offset = 0
        for line in wrapped:
            p.setFont(value_font, value_size)
            p.drawString(text_x + 140, y - offset, line)
            offset += (value_size + 3)
        return y - max(18, offset) - 6

    # Dibujar campos
    p.setFont("Helvetica", 12)
    p.drawString(text_x, cur_y, "Has sido aceptado en el evento:")
    cur_y -= 18
    # Nombre del evento (wrap, tamaño mayor)
    p.setFont("Helvetica-Bold", 13)
    event_lines = simpleSplit(str(inscripcion.evento.nombre), "Helvetica-Bold", 13, text_area_width)
    for line in event_lines:
        p.drawString(text_x, cur_y, line)
        cur_y -= 16
    cur_y -= 8

    # Datos alineados
    cur_y = draw_label_value("Fecha de inicio:", inscripcion.evento.fecha_inicio, cur_y, "Helvetica", 11, "Helvetica-Bold", 11)
    cur_y = draw_label_value("Fecha de finalización:", inscripcion.evento.fecha_fin, cur_y, "Helvetica", 11, "Helvetica-Bold", 11)
    cur_y = draw_label_value("Lugar:", inscripcion.evento.lugar, cur_y, "Helvetica", 11, "Helvetica-Bold", 11)
    cur_y = draw_label_value("Asistente:", f"{inscripcion.usuario.first_name} {inscripcion.usuario.last_name} ({inscripcion.usuario.email})", cur_y, "Helvetica", 11, "Helvetica-Bold", 11)

    # Dibujar elemento decorativo: franja lateral suave
    try:
        p.setFillColorRGB(0.94, 0.98, 0.97)
        p.rect(36, 36, 28, height-72, stroke=0, fill=1)
    except Exception:
        pass

    # Sello decorativo en la esquina inferior izquierda
    try:
        seal_x = box_x + 36
        seal_y = 80
        seal_r = 40
        p.setFillColorRGB(0.02, 0.45, 0.36)
        p.circle(seal_x, seal_y, seal_r, stroke=0, fill=1)
        p.setFillColorRGB(1, 1, 1)
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(seal_x, seal_y+4, "SENA")
        p.setFont("Helvetica", 7)
        p.drawCentredString(seal_x, seal_y-10, "Validado")
    except Exception:
        pass

    # Generar QR y colocarlo mucho más abajo (debajo de la caja de contenido)
    qr_data = f"Evento: {inscripcion.evento.nombre} | Asistente: {inscripcion.usuario.first_name} {inscripcion.usuario.last_name} | Email: {inscripcion.usuario.email} | Estado: {inscripcion.estado}"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)
    qr_size = 170
    qr_x = box_x + box_w - qr_size - 24
    # Colocar QR debajo de la caja, con margen inferior
    qr_y = box_y - qr_size - 30
    # Si no hay espacio suficiente para el QR debajo, desplazar hacia el centro inferior
    if qr_y < 60:
        qr_y = 60
        qr_x = box_x + (box_w - qr_size) / 2
    try:
        p.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')
    except Exception:
        qr_pil = Image.open(qr_buffer)
        p.drawInlineImage(qr_pil, qr_x, qr_y, qr_size, qr_size)

    # Etiqueta simple bajo el QR
    try:
        p.setFont("Helvetica", 9)
        p.setFillColorRGB(0.12, 0.12, 0.12)
        p.drawCentredString(qr_x + qr_size/2, qr_y - 12, "Código QR de verificación")
    except Exception:
        pass

    # Pie con nota
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColorRGB(0.3, 0.3, 0.3)
    p.drawCentredString(width/2, 40, "Presenta este comprobante en la entrada del evento. Código QR válido como identificación.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')

# ----------- Vistas por rol -----------

@login_required
def inicio_superadmin(request):
    return render(request, 'usuarios/inicio_superadmin.html')


def vista_admin(request):
    if request.user.rol != 'admin':
        return HttpResponse("No tienes permisos para acceder a esta página.", status=403)
    # Lógica solo para admin
    return render(request, 'usuarios/inicio_admin.html')
@login_required
def inicio_admin(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    mensaje_evento_creado = None
    if request.session.pop('evento_creado_pendiente', False):
        mensaje_evento_creado = 'Evento creado correctamente. Espera la aprobación del superadministrador.'
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        eventos = Evento.objects.filter(creador=request.user, estado='aceptado')
    else:
        eventos = Evento.objects.all()
    return render(request, 'usuarios/inicio_admin.html', {'eventos': eventos, 'mensaje_evento_creado': mensaje_evento_creado})

# ----------- Flujo multi-paso para envío de correos -----------
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods

@login_required
def seleccionar_evento_envio_correo(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        eventos = Evento.objects.filter(creador=request.user, estado='aceptado')
    else:
        eventos = Evento.objects.all()
    return render(request, 'usuarios/seleccionar_evento_envio_correo.html', {'eventos': eventos})

@login_required
def seleccionar_rol_envio_correo(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    # Puedes personalizar los roles disponibles aquí
    roles = [
        ('participante', 'Participantes'),
        ('evaluador', 'Evaluadores'),
        ('asistente', 'Asistentes'),
    ]
    return render(request, 'usuarios/seleccionar_rol_envio_correo.html', {'evento': evento, 'roles': roles})

@login_required
def seleccionar_usuarios_envio_correo(request, evento_id, rol):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    usuarios = []
    if rol == 'participante':
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='participante')
        usuarios = [insc.usuario for insc in inscripciones]
    elif rol == 'evaluador':
        from eventos.models import EvaluadorEvento
        rels = EvaluadorEvento.objects.filter(evento=evento)
        usuarios = [rel.evaluador.usuario for rel in rels]
    elif rol == 'asistente':
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente')
        usuarios = [insc.usuario for insc in inscripciones]
    enviados = False
    if request.method == 'POST':
        if 'enviar_certificados_participacion' in request.POST and rol == 'participante':
            seleccionados = request.POST.getlist('usuarios')
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from io import BytesIO
            from django.core.mail import EmailMessage
            for usuario_id in seleccionados:
                usuario = next((u for u in usuarios if str(u.id) == usuario_id), None)
                if usuario:
                    # Buscar inscripción
                    inscripcion = InscripcionEvento.objects.filter(evento=evento, usuario=usuario).first()
                    if inscripcion:
                        buffer = BytesIO()
                        c = canvas.Canvas(buffer, pagesize=letter)
                        width, height = letter
                        c.setFont("Helvetica-Bold", 20)
                        c.drawCentredString(width/2, height-100, "Certificado de Participación")
                        c.setFont("Helvetica", 14)
                        c.drawCentredString(width/2, height-150, f"Se certifica que {usuario.first_name} {usuario.last_name}")
                        c.drawCentredString(width/2, height-180, f"participó en el evento: {evento.nombre}")
                        c.drawCentredString(width/2, height-210, f"Fecha: {evento.fecha_inicio} al {evento.fecha_fin}")
                        c.drawCentredString(width/2, height-240, f"Lugar: {evento.lugar}")
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(width/2, height-300, "¡Gracias por tu participación!")
                        c.save()
                        buffer.seek(0)
                        email = EmailMessage(
                            subject=f"Certificado de Participación - {evento.nombre}",
                            body=f"Adjunto encontrarás tu certificado de participación en el evento '{evento.nombre}'.",
                            to=[usuario.email]
                        )
                        email.attach(f"Certificado_{evento.nombre}_{usuario.first_name}.pdf", buffer.getvalue(), 'application/pdf')
                        email.send()
            enviados = True
        else:
            seleccionados = request.POST.getlist('usuarios')
            request.session['envio_correo_usuarios'] = seleccionados
            request.session['envio_correo_evento_id'] = evento_id
            request.session['envio_correo_rol'] = rol
            return redirect('redactar_envio_correo')
    return render(request, 'usuarios/seleccionar_usuarios_envio_correo.html', {'evento': evento, 'usuarios': usuarios, 'rol': rol, 'enviados': enviados})

@login_required
def redactar_envio_correo(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    usuarios_ids = request.session.get('envio_correo_usuarios', [])
    evento_id = request.session.get('envio_correo_evento_id')
    rol = request.session.get('envio_correo_rol')
    if not usuarios_ids or not evento_id or not rol:
        messages.error(request, "Faltan datos para el envío de correos.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    usuarios = Usuario.objects.filter(id__in=usuarios_ids)
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        emails = [u.email for u in usuarios]
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
            emails,
            fail_silently=False
        )
        messages.success(request, f"Correos enviados a {len(emails)} usuarios.")
        # Limpiar sesión
        for key in ['envio_correo_usuarios', 'envio_correo_evento_id', 'envio_correo_rol']:
            if key in request.session:
                del request.session[key]
        return redirect('inicio_admin')
    return render(request, 'usuarios/redactar_envio_correo.html', {'evento': evento, 'usuarios': usuarios, 'rol': rol})

# ----------- Crear y editar eventos -----------
from eventos.forms import EventoForm

@login_required
def crear_evento(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para crear eventos.")
        return redirect('inicio_admin')
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento creado exitosamente.")
            return redirect('inicio_admin')
    else:
        form = EventoForm()
    return render(request, 'usuarios/crear_evento.html', {'form': form})

@login_required
def editar_evento(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para editar eventos.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, "Evento editado exitosamente.")
            return redirect('inicio_admin')
    else:
        form = EventoForm(instance=evento)
    return render(request, 'usuarios/editar_evento.html', {'form': form, 'evento': evento})
@login_required
def lista_eventos_evaluadores(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    if hasattr(request.user, 'rol') and request.user.rol == 'admin':
        eventos = Evento.objects.filter(creador=request.user)
    else:
        eventos = Evento.objects.all()
    for evento in eventos:
        evento.evaluadores_pendientes = evento.evaluadores_asignados.filter(estado='pendiente')
    return render(request, 'usuarios/lista_eventos_evaluadores.html', {'eventos': eventos})

# filepath: c:\Users\laspi\OneDrive\Desktop\PROYECTO DJANGO EVENTSOFT V10\eventsoft\usuarios\views.py
@login_required
def inicio_evaluador(request):
    evaluador = request.user.evaluador  # Suponiendo que el usuario tiene un perfil de evaluador
    evaluador_eventos = EvaluadorEvento.objects.filter(evaluador=evaluador)

    return render(request, 'usuarios/inicio_evaluador.html', {
        'usuario': request.user,
        'evaluador_eventos': evaluador_eventos,
    })

@login_required
def inicio_asistente(request):
    usuario = request.user
    if usuario.rol != 'asistente':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    inscripciones = InscripcionEvento.objects.filter(usuario=usuario)
    return render(request, 'usuarios/mis_inscripciones.html', {
        'inscripciones': inscripciones
    })

# ----------- Vistas de administración de eventos -----------
# VOLVER ADMIN NOTA DE ENDER
@login_required
def eventos_cancelacion_admin(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.filter(creador=request.user)
    return render(request, 'usuarios/eventos_cancelacion_admin.html', {'eventos': eventos})

@login_required
def cancelar_evento(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para cancelar eventos.")
        return redirect('eventos_cancelacion_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, f"El evento '{evento.nombre}' ha sido eliminado.")
    return redirect('eventos_cancelacion_admin')

@login_required
def eventos_programacion_admin(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.filter(creador=request.user)
    return render(request, 'usuarios/eventos_programacion_admin.html', {'eventos': eventos})

@login_required
def cargar_programacion_evento(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('eventos_programacion_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = ProgramacionEventoForm(request.POST)
        if form.is_valid():
            programacion = form.save(commit=False)
            programacion.evento = evento
            programacion.save()
            messages.success(request, "Programación cargada correctamente.")
            return redirect('eventos_programacion_admin')
    else:
        form = ProgramacionEventoForm()
    return render(request, 'usuarios/cargar_programacion_evento.html', {'form': form, 'evento': evento})

# ----------- Vistas de gestión de inscripciones (admin) -----------

@login_required
def participantes_preinscritos_admin(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    inscripciones = InscripcionEvento.objects.filter(evento_id=evento_id, usuario__rol='participante')
    datos = []
    for inscripcion in inscripciones:
        documentos = DocumentoParticipante.objects.filter(inscripcion=inscripcion)
        datos.append({'inscripcion': inscripcion, 'documentos': documentos})
    return render(request, 'usuarios/participantes_preinscritos_admin.html', {'datos': datos})

@login_required
def evaluadores_preinscritos_admin(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    from eventos.models import EvaluadorEvento, Evento
    evento = get_object_or_404(Evento, id=evento_id)
    evaluadores_evento = evento.evaluadores_asignados.all()
    datos = []
    from inscripciones.models import InscripcionEvento
    from documentos.models import DocumentoParticipante
    for rel in evaluadores_evento:
        inscripcion = InscripcionEvento.objects.filter(usuario=rel.evaluador.usuario, evento=evento).first()
        documentos = DocumentoParticipante.objects.filter(inscripcion=inscripcion) if inscripcion else []
        datos.append({'rel': rel, 'inscripcion': inscripcion, 'documentos': documentos})
    return render(request, 'usuarios/evaluadores_preinscritos_admin.html', {
        'evento': evento,
        'datos': datos
    })

@login_required
def aprobar_inscripcion_participante(request, inscripcion_id, nuevo_estado):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('/usuarios/login/')
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id, usuario__rol='participante')
    inscripcion.estado = nuevo_estado
    clave_generada = None
    if nuevo_estado == 'admitido':
        import random
        import string
        clave_generada = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        usuario = inscripcion.usuario
        # Solo permitir set_password si no es admin_evento
        if not hasattr(usuario, 'admin_evento'):
            usuario.set_password(clave_generada)
            usuario.save()
            # Sincronizar clave con Participante
            try:
                participante = usuario.participante
                participante.clave_temporal = clave_generada
                participante.save()
            except Exception:
                pass
    inscripcion.save()
    evento = inscripcion.evento
    if nuevo_estado == 'admitido' and clave_generada:
        # Enviar correo con la clave de acceso
        try:
            from proyectos.utils import enviar_correo_admision_participante
            participante = usuario.participante
            enviar_correo_admision_participante(participante, evento)
        except Exception as e:
            print(f"Error enviando correo de admisión: {e}")
        mensaje = f"¡Preinscripción exitosa!\nEvento: {evento.nombre}\n\nTu clave de acceso es: {clave_generada}\n\nGuárdala en un lugar seguro."
        return render(request, 'usuarios/preinscripcion_exitosa.html', {'evento': evento, 'mensaje': mensaje})
    else:
        messages.success(request, f"Inscripción actualizada a '{nuevo_estado}'.")
        return redirect('participantes_preinscritos_admin', evento_id=evento.id)

@login_required
def eventos_para_aprobar_participantes(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.filter(creador=request.user)
    return render(request, 'usuarios/eventos_para_aprobar_participantes.html', {'eventos': eventos})

@login_required
def lista_eventos_cambiar_participante(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.filter(creador=request.user)
    return render(request, 'usuarios/lista-eventos-cambiar-participante.html', {'eventos': eventos})

@login_required
def asistentes_inscritos_todos_eventos(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.filter(creador=request.user)
    datos = []
    for evento in eventos:
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente')
        datos.append({'evento': evento, 'inscripciones': inscripciones})
    return render(request, 'usuarios/asistentes_inscritos_todos_eventos.html', {'datos': datos})

@login_required
def lista_eventos_cambiar_estado(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    eventos = Evento.objects.filter(creador=request.user)
    return render(request, 'usuarios/eventos_asistente_estado.html', {'eventos': eventos})

@login_required
def cambiar_estado_asistente(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    evento.inscripciones_habilitadas = not evento.inscripciones_habilitadas
    evento.save()
    estado = "habilitadas" if evento.inscripciones_habilitadas else "deshabilitadas"
    return render(request, 'usuarios/cambiar_estado_asistente.html', {'evento': evento, 'estado': estado})

@login_required
def asistentes_inscritos_evento(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    evento = get_object_or_404(Evento, id=evento_id)
    inscripciones = InscripcionEvento.objects.filter(evento=evento)
    return render(request, 'usuarios/cambiar_estado_asistente.html', {'evento': evento, 'inscripciones': inscripciones})

@login_required
def cambiar_estado_asistente_evento(request, inscripcion_id, nuevo_estado):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_admin')
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id)
    inscripcion.estado = nuevo_estado
    inscripcion.save()
    return redirect('asistentes_inscritos_evento', evento_id=inscripcion.evento.id)

@login_required
def estadisticas_asistentes_evento(request):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.filter(creador=request.user)
    estadisticas = []
    for evento in eventos:
        total_asistentes = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente').count()
        admitidos = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente', estado='admitido').count()
        rechazados = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente', estado='rechazado').count()
        estadisticas.append({
            'evento': evento,
            'total': total_asistentes,
            'admitidos': admitidos,
            'rechazados': rechazados,
        })
    return render(request, 'usuarios/estadisticas_asistentes_evento.html', {'estadisticas': estadisticas})

@login_required
def ver_evaluaciones_evento(request, evento_id):
    usuario = request.user
    participante = getattr(usuario, 'participante', None)
    if not participante:
        return redirect('mis_inscripciones')
    proyectos = Proyecto.objects.filter(participantes=participante, evento_id=evento_id)
    evaluaciones = Evaluacion.objects.filter(proyecto__in=proyectos)
    evento = get_object_or_404(Evento, id=evento_id)
    return render(request, 'usuarios/ver_evaluaciones_evento.html', {
        'evento': evento,
        'proyectos': proyectos,
        'evaluaciones': evaluaciones
    })

@login_required
def eventos_gestion_instrumentos_admin(request):
    if not request.user.is_authenticated or request.user.rol != 'admin':
        from django.contrib import messages
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('/usuarios/login/')
    # Mostrar solo los eventos donde el usuario es admin (ajusta si tienes relación directa)
    eventos = Evento.objects.filter(creador=request.user)
    return render(request, 'usuarios/eventos_gestion_instrumentos_admin.html', {'eventos': eventos})


@login_required
def editar_info_evaluador(request, evento_id):
    usuario = request.user
    evento = get_object_or_404(Evento, id=evento_id)
    inscripcion = InscripcionEvento.objects.filter(usuario=usuario, evento=evento).first()
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
                    DocumentoParticipante.objects.create(
                        inscripcion=inscripcion,
                        archivo=nuevo_doc,
                        descripcion="Documento de preinscripción evaluador"
                    )
            return redirect('perfil_participante')
    else:
        form = PreinscripcionEvaluadorForm(initial={
            'nombre': usuario.first_name,
            'correo': usuario.email,
        })
    return render(request, 'usuarios/editar_info_evaluador.html', {
        'form': form,
        'documento': documento,
        'evento': evento
    })


@login_required
def descargar_comprobante_evaluador(request, evento_id):
    usuario = request.user
    try:
        evaluador = usuario.evaluador
    except Exception:
        return HttpResponse("No eres evaluador.", status=403)
    ev_evento = EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id, estado='admitido').first()
    if not ev_evento:
        return HttpResponse("No tienes permiso para descargar el comprobante.", status=403)
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 14)
    p.drawString(100, 810, f"Comprobante de inscripción como Evaluador")
    p.setFont("Helvetica", 12)
    p.drawString(100, 790, f"Evento: {ev_evento.evento.nombre}")
    p.drawString(100, 770, f"Fecha de inicio: {ev_evento.evento.fecha_inicio}")
    p.drawString(100, 750, f"Fecha de finalización: {ev_evento.evento.fecha_fin}")
    p.drawString(100, 730, f"Evaluador: {usuario.first_name} {usuario.last_name} ({usuario.email})")
    qr_data = f"Evento: {ev_evento.evento.nombre} | Evaluador: {usuario.first_name} {usuario.last_name} | Email: {usuario.email} | Estado: {ev_evento.estado}"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_pil = Image.open(qr_buffer)
    p.drawInlineImage(qr_pil, 100, 600, 100, 100)
    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')


@login_required
def detalle_evento_evaluador(request, evento_id):
    usuario = request.user
    try:
        evaluador = usuario.evaluador
    except Exception:
        return HttpResponse("No eres evaluador.", status=403)
    # Solo permitir si es evaluador de ese evento
    if not EvaluadorEvento.objects.filter(evaluador=evaluador, evento_id=evento_id).exists():
        return HttpResponse("No tienes permiso para ver este evento.", status=403)
    evento = Evento.objects.get(id=evento_id)
    return render(request, 'usuarios/detalle_evento_evaluador.html', {'evento': evento})

@login_required
def ver_info_tecnica_participante(request, evento_id):
    evento = Evento.objects.get(id=evento_id)
    info_tecnica = InfoTecnicaEvento.objects.filter(evento=evento)
    return render(request, 'eventos/ver_info_tecnica_participante.html', {
        'evento': evento,
        'info_tecnica': info_tecnica
    })




def sin_permiso(request):
    return render(request, 'usuarios/sin_permiso.html')

@login_required
def aprobar_inscripcion_evaluador(request, evaluador_evento_id, nuevo_estado):
    if request.user.rol != 'admin':
        from django.contrib import messages
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('login')
    from eventos.models import EvaluadorEvento
    evaluador_evento = get_object_or_404(EvaluadorEvento, id=evaluador_evento_id)
    usuario = evaluador_evento.evaluador.usuario
    # Generar clave dinámica si es admitido
    clave_generada = None
    if request.method == 'POST':
        evaluador_evento.estado = nuevo_estado
        evaluador_evento.save()
        if nuevo_estado == 'admitido':
            import random
            import string
            clave_generada = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            # Solo permitir set_password si no es admin_evento
            if not hasattr(usuario, 'admin_evento'):
                usuario.set_password(clave_generada)
            usuario.save()
        # Enviar correo
        from django.core.mail import send_mail
        asunto = f"Resultado de preinscripción como evaluador en el evento {evaluador_evento.evento.nombre}"
        if nuevo_estado == 'admitido':
            mensaje = f"¡Felicidades! Has sido admitido como evaluador en el evento '{evaluador_evento.evento.nombre}'.\n\nTu clave de acceso es: {clave_generada}\n\nPuedes acceder al panel de evaluador con tu correo y esta clave."
        else:
            mensaje = f"Lamentamos informarte que no has sido admitido como evaluador en el evento '{evaluador_evento.evento.nombre}'."
        send_mail(
            asunto,
            mensaje,
            None,
            [usuario.email],
            fail_silently=False
        )
        from django.contrib import messages
        messages.success(request, f"Evaluador actualizado a '{nuevo_estado}'. Se ha enviado un correo a {usuario.email}.")
    return redirect('lista_eventos_evaluadores')

@login_required
def crear_inscripcion_evaluador(request, evento_id):
    usuario = request.user
    evento = get_object_or_404(Evento, id=evento_id)
    usuario.rol = 'evaluador'
    usuario.save()
    # Crear Evaluador si no existe
    evaluador, _ = Evaluador.objects.get_or_create(usuario=usuario)
    # Crear relación EvaluadorEvento si no existe
    from eventos.models import EvaluadorEvento
    EvaluadorEvento.objects.get_or_create(evaluador=evaluador, evento=evento, defaults={'estado': 'pendiente'})
    return redirect('editar_info_evaluador', evento_id=evento.id)
@login_required
def admin_certificados_evento(request, evento_id):
    from proyectos.models import Proyecto
    from usuarios.models import Participante
    from eventos.models import Evento
    evento = get_object_or_404(Evento, id=evento_id)
    participantes = Participante.objects.filter(proyectos__evento=evento).distinct()
    enviados = False
    if request.method == 'POST':
        for participante in participantes:
            if request.POST.get(f'seleccionado_{participante.id}'):
                puesto = request.POST.get(f'puesto_{participante.id}')
                if puesto:
                    from eventos.views import enviar_certificado_reconocimiento
                    enviar_certificado_reconocimiento(participante, evento, puesto)
        enviados = True
    return render(request, 'usuarios/admin_certificados_evento.html', {
        'participantes': participantes,
        'evento_id': evento_id,
        'enviados': enviados
    })

import os
from django.http import HttpResponse
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from eventos.models import Evento

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

# --------- SUPER ADMIN ----------------
@login_required
def eventos_cancelacion_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all()
    return render(request, 'usuarios/eventos_cancelacion_superadmin.html', {'eventos': eventos})

@login_required
def cancelar_evento_superadmin(request, evento_id):
    if request.user.rol != 'admin':
        messages.error(request, "No tienes permisos para cancelar eventos.")
        return redirect('eventos_cancelacion_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        messages.success(request, f"El evento '{evento.nombre}' ha sido eliminado.")
    return redirect('eventos_cancelacion_superadmin')

@login_required
def lista_eventos_cambiar_participante_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all()
    return render(request, 'usuarios/lista-eventos-cambiar-participante-superadmin.html', {'eventos': eventos})

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

@login_required
def asistentes_inscritos_todos_eventos_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all()
    datos = []
    for evento in eventos:
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente')
        datos.append({'evento': evento, 'inscripciones': inscripciones})
    return render(request, 'usuarios/asistentes_inscritos_todos_eventos_superadmin.html', {'datos': datos})

@login_required
def eventos_programacion_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all()
    return render(request, 'usuarios/eventos_programacion_superadmin.html', {'eventos': eventos})

@login_required
def cargar_programacion_evento_superadmin(request, evento_id):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('eventos_programacion_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    if request.method == 'POST':
        form = ProgramacionEventoForm(request.POST)
        if form.is_valid():
            programacion = form.save(commit=False)
            programacion.evento = evento
            programacion.save()
            messages.success(request, "Programación cargada correctamente.")
            return redirect('eventos_programacion_admin')
    else:
        form = ProgramacionEventoForm()
    return render(request, 'usuarios/cargar_programacion_evento_superadmin.html', {'form': form, 'evento': evento})

@login_required
def asistentes_inscritos_evento_superadmin(request, evento_id):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    inscripciones = InscripcionEvento.objects.filter(evento=evento)
    return render(request, 'usuarios/cambiar_estado_asistente_superadmin.html', {'evento': evento, 'inscripciones': inscripciones})

@login_required
def lista_eventos_cambiar_estado_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    eventos = Evento.objects.all()
    return render(request, 'usuarios/eventos_asistente_estado_superadmin.html', {'eventos': eventos})

@login_required
def cambiar_estado_asistente_evento_superadmin(request, inscripcion_id, nuevo_estado):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    inscripcion = get_object_or_404(InscripcionEvento, id=inscripcion_id)
    inscripcion.estado = nuevo_estado
    inscripcion.save()
    return redirect('asistentes_inscritos_evento_superadmin', evento_id=inscripcion.evento.id)

@login_required
def estadisticas_asistentes_evento_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all()
    estadisticas = []
    for evento in eventos:
        total_asistentes = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente').count()
        admitidos = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente', estado='admitido').count()
        rechazados = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente', estado='rechazado').count()
        estadisticas.append({
            'evento': evento,
            'total': total_asistentes,
            'admitidos': admitidos,
            'rechazados': rechazados,
        })
    return render(request, 'usuarios/estadisticas_asistentes_evento_superadmin.html', {'estadisticas': estadisticas})

@login_required
def eventos_gestion_instrumentos_superadmin(request):
    if not request.user.is_authenticated or request.user.rol != 'superadmin':
        from django.contrib import messages
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('/usuarios/login/')
    # Mostrar solo los eventos donde el usuario es admin (ajusta si tienes relación directa)
    eventos = Evento.objects.all()  # Filtra si hay relación admin-evento
    return render(request, 'usuarios/eventos_gestion_instrumentos_superadmin.html', {'eventos': eventos})

@login_required
def superadmin_certificados_evento(request, evento_id):
    from proyectos.models import Proyecto
    from usuarios.models import Participante
    from eventos.models import Evento
    evento = get_object_or_404(Evento, id=evento_id)
    participantes = Participante.objects.filter(proyecto__evento=evento).distinct()
    enviados = False
    if request.method == 'POST':
        for participante in participantes:
            if request.POST.get(f'seleccionado_{participante.id}'):
                puesto = request.POST.get(f'puesto_{participante.id}')
                if puesto:
                    from eventos.views import enviar_certificado_reconocimiento
                    enviar_certificado_reconocimiento(participante, evento, puesto)
        enviados = True
    return render(request, 'usuarios/superadmin_certificados_evento.html', {
        'participantes': participantes,
        'evento_id': evento_id,
        'enviados': enviados
    })

@login_required
def lista_eventos_configurar_certificados_superadmin(request):
    if not hasattr(request.user, 'rol') or request.user.rol != 'superadmin':
        storage = messages.get_messages(request)
        list(storage)
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all().order_by('-fecha_inicio')
    return render(request, 'usuarios/lista_eventos_configurar_certificados_superadmin.html', {'eventos': eventos})


def configurar_certificados_evento_superadmin(request, evento_id):
    if not request.user.is_authenticated or getattr(request.user, 'rol', None) != 'superadmin':
        from django.http import HttpResponse
        return HttpResponse('No tienes permisos para configurar certificados.', status=403)
    evento = get_object_or_404(Evento, id=evento_id)
    try:
        config = evento.configuracion_certificado
    except ConfiguracionCertificadoEvento.DoesNotExist:
        config = None

    if request.method == 'POST':
        form = ConfiguracionCertificadoEventoForm(request.POST, instance=config)
        if form.is_valid():
            config = form.save(commit=False)
            config.evento = evento
            config.save()
            return render(request, 'usuarios/configurar_certificados_evento_superadmin.html', {
                'form': form,
                'evento_id': evento_id,
                'guardado': True
            })
    else:
        form = ConfiguracionCertificadoEventoForm(instance=config)

    return render(request, 'usuarios/configurar_certificados_evento_superadmin.html', {
        'form': form,
        'evento_id': evento_id
    })

@login_required
def seleccionar_evento_envio_correo_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    eventos = Evento.objects.all()
    return render(request, 'usuarios/seleccionar_evento_envio_correo_superadmin.html', {'eventos': eventos})

@login_required
def seleccionar_rol_envio_correo_superadmin(request, evento_id):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    # Puedes personalizar los roles disponibles aquí
    roles = [
        ('participante', 'Participantes'),
        ('evaluador', 'Evaluadores'),
        ('asistente', 'Asistentes'),
    ]
    return render(request, 'usuarios/seleccionar_rol_envio_correo_superadmin.html', {'evento': evento, 'roles': roles})

@login_required
def seleccionar_usuarios_envio_correo_superadmin(request, evento_id, rol):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    usuarios = []
    if rol == 'participante':
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='participante')
        usuarios = [insc.usuario for insc in inscripciones]
    elif rol == 'evaluador':
        from eventos.models import EvaluadorEvento
        rels = EvaluadorEvento.objects.filter(evento=evento)
        usuarios = [rel.evaluador.usuario for rel in rels]
    elif rol == 'asistente':
        inscripciones = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente')
        usuarios = [insc.usuario for insc in inscripciones]
    enviados = False
    if request.method == 'POST':
        if 'enviar_certificados_participacion' in request.POST and rol == 'participante':
            seleccionados = request.POST.getlist('usuarios')
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from io import BytesIO
            from django.core.mail import EmailMessage
            for usuario_id in seleccionados:
                usuario = next((u for u in usuarios if str(u.id) == usuario_id), None)
                if usuario:
                    # Buscar inscripción
                    inscripcion = InscripcionEvento.objects.filter(evento=evento, usuario=usuario).first()
                    if inscripcion:
                        buffer = BytesIO()
                        c = canvas.Canvas(buffer, pagesize=letter)
                        width, height = letter
                        c.setFont("Helvetica-Bold", 20)
                        c.drawCentredString(width/2, height-100, "Certificado de Participación")
                        c.setFont("Helvetica", 14)
                        c.drawCentredString(width/2, height-150, f"Se certifica que {usuario.first_name} {usuario.last_name}")
                        c.drawCentredString(width/2, height-180, f"participó en el evento: {evento.nombre}")
                        c.drawCentredString(width/2, height-210, f"Fecha: {evento.fecha_inicio} al {evento.fecha_fin}")
                        c.drawCentredString(width/2, height-240, f"Lugar: {evento.lugar}")
                        c.setFont("Helvetica", 12)
                        c.drawCentredString(width/2, height-300, "¡Gracias por tu participación!")
                        c.save()
                        buffer.seek(0)
                        email = EmailMessage(
                            subject=f"Certificado de Participación - {evento.nombre}",
                            body=f"Adjunto encontrarás tu certificado de participación en el evento '{evento.nombre}'.",
                            to=[usuario.email]
                        )
                        email.attach(f"Certificado_{evento.nombre}_{usuario.first_name}.pdf", buffer.getvalue(), 'application/pdf')
                        email.send()
            enviados = True
        else:
            seleccionados = request.POST.getlist('usuarios')
            request.session['envio_correo_usuarios'] = seleccionados
            request.session['envio_correo_evento_id'] = evento_id
            request.session['envio_correo_rol'] = rol
            return redirect('redactar_envio_correo_superadmin')
    return render(request, 'usuarios/seleccionar_usuarios_envio_correo_superadmin.html', {'evento': evento, 'usuarios': usuarios, 'rol': rol, 'enviados': enviados})

@login_required
def redactar_envio_correo_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    usuarios_ids = request.session.get('envio_correo_usuarios', [])
    evento_id = request.session.get('envio_correo_evento_id')
    rol = request.session.get('envio_correo_rol')
    if not usuarios_ids or not evento_id or not rol:
        messages.error(request, "Faltan datos para el envío de correos.")
        return redirect('inicio_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    usuarios = Usuario.objects.filter(id__in=usuarios_ids)
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        emails = [u.email for u in usuarios]
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
            emails,
            fail_silently=False
        )
        messages.success(request, f"Correos enviados a {len(emails)} usuarios.")
        # Limpiar sesión
        for key in ['envio_correo_usuarios', 'envio_correo_evento_id', 'envio_correo_rol']:
            if key in request.session:
                del request.session[key]
        return redirect('inicio_superadmin')
    return render(request, 'usuarios/redactar_envio_correo_superadmin.html', {'evento': evento, 'usuarios': usuarios, 'rol': rol})

@login_required
def enviar_correo_masivo_evento_superadmin(request, evento_id):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')
    evento = get_object_or_404(Evento, id=evento_id)
    # Participantes
    insc_part = InscripcionEvento.objects.filter(evento=evento, usuario__rol='participante')
    usuarios_part = [insc.usuario for insc in insc_part]
    # Asistentes
    insc_asist = InscripcionEvento.objects.filter(evento=evento, usuario__rol='asistente')
    usuarios_asist = [insc.usuario for insc in insc_asist]
    # Evaluadores
    from eventos.models import EvaluadorEvento
    rels_eval = EvaluadorEvento.objects.filter(evento=evento)
    usuarios_eval = [rel.evaluador.usuario for rel in rels_eval]
    usuarios = list(set(usuarios_part + usuarios_asist + usuarios_eval))
    enviados = False
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')
        emails = [u.email for u in usuarios if u.email]
        if emails and asunto and mensaje:
            from django.core.mail import send_mail
            from django.conf import settings
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
                emails,
                fail_silently=False
            )
            enviados = True
            messages.success(request, f"Correos enviados a {len(emails)} usuarios del evento.")
        else:
            messages.error(request, "Faltan datos o no hay destinatarios.")
    return render(request, 'usuarios/seleccionar_rol_envio_correo_superadmin.html', {
        'evento': evento,
        'roles': [
            ('participante', 'Participantes'),
            ('evaluador', 'Evaluadores'),
            ('asistente', 'Asistentes'),
        ],
        'enviados': enviados
    })

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
    return render(request, 'usuarios/editar_evento_superadmin.html', {'form': form, 'evento': evento})

@login_required
def inicio_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para ver esta página.")
        return redirect('/usuarios/login/')
    eventos = Evento.objects.all()
    return render(request, 'usuarios/inicio_superadmin.html', {'eventos': eventos})

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Usuario, AdministradorEvento
from .models_codigo_acceso import EventAdminAccessCode


@login_required
def crear_administrador_superadmin(request):
    if request.user.rol != 'superadmin':
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect('inicio_superadmin')

    if request.method == 'POST':
        import random
        import string
        email = request.POST.get('email')
        nombre = request.POST.get('nombre')
        estado = request.POST.get('estado', 'pendiente')
        max_events = request.POST.get('max_events')
        expires_at = request.POST.get('expires_at')

    # Generar la clave SOLO UNA VEZ y usarla para todo, usando secrets.token_urlsafe(8) para mayor seguridad y unicidad
        import secrets
        clave_unica = secrets.token_urlsafe(8)

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "Ya existe un usuario con este correo electrónico.")
        else:
            usuario = Usuario(
                email=email,
                username=email,  # username igual al email para compatibilidad
                first_name=nombre,
                rol='admin',
                is_active=True  # Solo para admin
            )
            usuario.set_password(clave_unica)
            usuario.save()
            AdministradorEvento.objects.create(usuario=usuario, estado=estado)
            EventAdminAccessCode.objects.create(
                admin=usuario,
                code=clave_unica,  # El código de acceso es la misma clave generada
                max_events=int(max_events) if max_events else None,
                expires_at=expires_at if expires_at else None
            )
            # Enviar correo con la clave generada
            from django.core.mail import send_mail
            mensaje_correo = f"Hola {nombre},\n\nHas sido registrado como Administrador de Evento en la plataforma.\n\nTu usuario es: {email}\n\nTu clave de acceso es: {clave_unica}\n\nPor favor, accede al sistema y cambia tu contraseña en el primer inicio de sesión.\n\n¡Éxitos en la gestión de tu evento!"
            send_mail(
                'Registro como Administrador de Evento',
                mensaje_correo,
                None,
                [email],
                fail_silently=False
            )
            return render(request, 'usuarios/crear_administrador_superadmin.html', {
                'clave_generada': clave_unica,
                'admin_email': email,
                'admin_nombre': nombre,
                'creado': True
            })

    return render(request, 'usuarios/crear_administrador_superadmin.html')