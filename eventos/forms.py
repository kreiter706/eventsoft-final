from django import forms
from .models import PresentacionEvento

class PresentacionEventoForm(forms.ModelForm):
    class Meta:
        model = PresentacionEvento
        fields = ['nombre', 'archivo']
from .models import ConfiguracionCertificadoEvento

# Formulario para configuración de certificados por evento
class ConfiguracionCertificadoEventoForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionCertificadoEvento
        fields = [
            'nombre_evento',
            'fecha_inicio_evento',
            'fecha_fin_evento',
            'lugar_evento',
            'organizador_evento',
            'mensaje_certificado',
        ]
        widgets = {
            'fecha_inicio_evento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin_evento': forms.DateInput(attrs={'type': 'date'}),
        }
from .models import Evento, ItemInstrumento, InstrumentoEvaluacion
from datetime import date
from usuarios.models import Usuario
from .models import InfoTecnicaEvento
from inscripciones.models import InscripcionEvento
from .models import Asistente  # Asegúrate de tener este modelo
from django.shortcuts import render, get_object_or_404, redirect

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        exclude = ['creador', 'estado']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
            'imagen': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_fecha_inicio(self):
        fecha_inicio = self.cleaned_data['fecha_inicio']
        if fecha_inicio < date.today():
            raise forms.ValidationError("La fecha de inicio no puede ser en el pasado.")
        return fecha_inicio

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            self.add_error('fecha_fin', "La fecha de fin no puede ser anterior a la fecha de inicio.")

class RegistroVisitanteEventoForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    correo = forms.EmailField(label="Correo electrónico")
    soporte_pago = forms.FileField(label="Soporte de pago", required=False)
#-------------------------------------------------------------------------------------
class PreinscripcionParticipanteForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    correo = forms.EmailField(label="Correo electrónico")
    documento = forms.FileField(label="Documento requerido")
    comprobante_pago = forms.FileField(label="Comprobante de pago", required=False)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)
#-------------------------------------------------------------------------------------

class RegistroAsistenteEventoForm(forms.ModelForm):
    documento = forms.FileField(label="Documento (obligatorio)")  

    class Meta:
        model = Asistente
        fields = ['nombre', 'correo', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }

class ItemInstrumentoForm(forms.ModelForm):
    class Meta:
        model = ItemInstrumento
        fields = ['nombre', 'descripcion', 'puntaje_maximo', 'peso_porcentaje']

    def clean(self):
        cleaned_data = super().clean()
        peso = cleaned_data.get('peso_porcentaje')
        instrumento = self.instance.instrumento if self.instance.pk else self.initial.get('instrumento')
        if instrumento:
            from eventos.models import ItemInstrumento
            items = ItemInstrumento.objects.filter(instrumento=instrumento)
            suma = sum([float(item.peso_porcentaje) for item in items])
            if self.instance.pk:
                suma -= float(self.instance.peso_porcentaje)
            if peso is not None:
                suma += float(peso)
            if suma > 100:
                raise forms.ValidationError("La suma de los pesos de los ítems no puede superar el 100%.")
        return cleaned_data

class InstrumentoEvaluacionForm(forms.ModelForm):
    class Meta:
        model = InstrumentoEvaluacion
        fields = ['nombre', 'tipo', 'descripcion']



#-------------------------------------------Evaluador---------------------------------------------------
class PreinscripcionEvaluadorForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    documento = forms.FileField(label="Documento de soporte (CV, certificaciones, etc.)")


class InfoTecnicaEventoForm(forms.ModelForm):
    class Meta:
        model = InfoTecnicaEvento
        fields = ['descripcion', 'archivo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }