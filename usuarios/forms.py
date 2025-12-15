from django import forms
from .models import Usuario, Participante, Evaluador, Asistente, AdministradorEvento
from eventos.models import ProgramacionEvento  
from django import forms


class CrearUsuarioForm(forms.ModelForm):
    rol = forms.ChoiceField(choices=[
        ('participante', 'Participante'),
        ('evaluador', 'Evaluador'),
        ('asistente', 'Asistente'),
        ('admin_evento', 'Administrador de Evento')
    ])

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'rol']
        

class ProgramacionEventoForm(forms.ModelForm):
    class Meta:
        model = ProgramacionEvento
        fields = ['titulo_actividad', 'descripcion', 'fecha', 'hora_inicio', 'hora_fin', 'lugar']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }
from django import forms
# ...existing code...

class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Correo electrónico")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)