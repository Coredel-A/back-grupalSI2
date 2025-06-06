from django.contrib import admin
from .models import Rol, Permiso

@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    list_display = ('codename', 'descripcion')
    search_fields = ('codename',)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    filter_horizontal = ('permisos',)  # Para seleccionar permisos más fácilmente
