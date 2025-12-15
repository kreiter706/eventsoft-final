
from django.shortcuts import render, redirect, get_object_or_404


from .forms import ProyectoRegistroForm
from eventos.forms_grupo import ParticipanteGrupoForm, formset_factory
from usuarios.models import Usuario
from documentos.models import DocumentoParticipante
from eventos.models import Evento

def registrar_proyecto(request, evento_id):
	evento = get_object_or_404(Evento, id=evento_id)
	ParticipanteGrupoFormSet = formset_factory(ParticipanteGrupoForm, extra=1, min_num=1, validate_min=True)
	mensaje = None
	if request.method == 'POST':
		form = ProyectoRegistroForm(request.POST, request.FILES)
		formset = ParticipanteGrupoFormSet(request.POST, request.FILES)
		form.fields['evento'].initial = evento.id
		if form.is_valid() and formset.is_valid():
			proyecto = form.save(commit=False)
			proyecto.evento = evento
			proyecto.save()
			participantes_objs = []
			import string, random
			for participante_form in formset:
				nombre = participante_form.cleaned_data['nombre']
				correo = participante_form.cleaned_data['correo']
				documento = participante_form.cleaned_data['documento']
				comprobante_pago = participante_form.cleaned_data.get('comprobante_pago')
				from usuarios.models import Participante as ParticipanteModel
				usuario, creado = Usuario.objects.get_or_create(email=correo, defaults={
					'username': correo,
					'first_name': nombre,
					'rol': 'participante',
				})
				if creado:
					import string, random
					password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
					usuario.set_password(password)
					usuario.rol = 'participante'
					usuario.save()
					participante_obj, _ = ParticipanteModel.objects.get_or_create(usuario=usuario)
					participante_obj.clave_temporal = password
					participante_obj.save()
				else:
					participante_obj, _ = ParticipanteModel.objects.get_or_create(usuario=usuario)
				participantes_objs.append(participante_obj)
				# Asociar documentos
				from inscripciones.models import InscripcionEvento
				inscripcion, _ = InscripcionEvento.objects.get_or_create(usuario=usuario, evento=evento)
				DocumentoParticipante.objects.create(
					inscripcion=inscripcion,
					archivo=documento,
					descripcion="Documento de preinscripción"
				)
				if evento.costo_inscripcion and comprobante_pago:
					DocumentoParticipante.objects.create(
						inscripcion=inscripcion,
						archivo=comprobante_pago,
						descripcion="Comprobante de pago"
					)
			for p in participantes_objs:
				proyecto.participantes.add(p)
			return redirect('detalle_evento', evento_id=evento.id)
	else:
		form = ProyectoRegistroForm(initial={'evento': evento.id})
		formset = ParticipanteGrupoFormSet()
	return render(request, 'proyectos/registrar_proyecto.html', {'form': form, 'formset': formset, 'evento': evento, 'mensaje': mensaje})
