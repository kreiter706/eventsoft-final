from django import forms
from .models_codigo_acceso import EventAdminAccessCode

class CambiarEstadoCodigoForm(forms.ModelForm):
    class Meta:
        model = EventAdminAccessCode
        fields = ['estado']
        labels = {
            'estado': 'Estado del código',
        }
        help_texts = {
            'estado': 'Elija "Activo" para habilitar el acceso, "Suspendido" para bloquear temporalmente, o "Cancelado" para anularlo permanentemente.'
        }
