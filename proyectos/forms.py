from django import forms
from .models import Proyecto
from usuarios.models import Participante

class ProyectoRegistroForm(forms.ModelForm):
    participantes = forms.ModelMultipleChoiceField(
        queryset=Participante.objects.filter(estado='admitido'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Selecciona los participantes del proyecto (inclúyete si es grupal)"
    )
    crear_nuevo = forms.BooleanField(
        required=False,
        label="Crear un nuevo proyecto (si no, puedes unirte a uno existente)"
    )

    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'archivo', 'participantes', 'evento']
        widgets = {
            'evento': forms.HiddenInput(),
        }
