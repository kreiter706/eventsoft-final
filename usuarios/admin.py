from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Participante, Evaluador, AdministradorEvento, Asistente
from .models_codigo_acceso import EventAdminAccessCode

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'rol'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'rol')}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')

admin.site.register(Usuario, CustomUserAdmin)
from django.contrib import admin
from .models import Participante


class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado', 'clave_temporal')

    def save_model(self, request, obj, form, change):
        # Siempre sincroniza la clave temporal con la contraseña real
        if obj.clave_temporal:
            obj.usuario.set_password(obj.clave_temporal)
            obj.usuario.save()
        super().save_model(request, obj, form, change)

admin.site.register(Participante, ParticipanteAdmin)
admin.site.register(Evaluador)
admin.site.register(AdministradorEvento)
admin.site.register(Asistente)

# Registro del modelo de código de acceso para administradores de evento
@admin.register(EventAdminAccessCode)
class EventAdminAccessCodeAdmin(admin.ModelAdmin):
    list_display = ('admin', 'code', 'max_events', 'expires_at', 'estado', 'is_valid')
    search_fields = ('admin__username', 'code')
    list_filter = ('expires_at', 'estado')

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'estado':
            formfield.help_text = 'Elija "Activo" para habilitar el acceso, "Suspendido" para bloquear temporalmente, o "Cancelado" para anularlo permanentemente.'
        return formfield