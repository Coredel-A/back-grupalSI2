from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    model = Usuario
    list_display = ('email', 'nombre', 'apellido', 'is_staff', 'is_active', 'establecimiento', 'especialidad', 'rol')
    list_filter = ('is_staff', 'is_active', 'establecimiento', 'especialidad')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('nombre', 'apellido', 'fecha_nacimiento', 'fecha_registro')}),
        ('Organización', {'fields': ('establecimiento', 'especialidad')}),
        ('Permisos', {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'password1', 'password2', 'establecimiento', 'especialidad', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
