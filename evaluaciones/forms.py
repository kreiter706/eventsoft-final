from django import forms
from .models import CalificacionParticipante

class CalificacionParticipanteForm(forms.ModelForm):
    class Meta:
        model = CalificacionParticipante
        fields = ['puntaje', 'observaciones']
