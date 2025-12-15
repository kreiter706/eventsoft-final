from django import forms
from django.forms import formset_factory

class ParticipanteGrupoForm(forms.Form):
    nombre = forms.CharField(max_length=100, label="Nombre")
    correo = forms.EmailField(label="Correo electrónico")
    documento = forms.FileField(label="Documento de identidad")
    # Eliminado campo de contraseña, ahora se genera automáticamente
    comprobante_pago = forms.FileField(label="Comprobante de pago", required=False)

# Para usar en la vista: ParticipanteGrupoFormSet = formset_factory(ParticipanteGrupoForm, extra=1, min_num=1, validate_min=True)
