from django.contrib import admin
from .models import Establecimiento, SucursalEspecialidad

class SucursalEspecialidadInline(admin.TabularInline):
    model = SucursalEspecialidad
    extra = 1

@admin.register(Establecimiento)
class EstablecimientoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_establecimiento', 'nivel', 'telefono', 'correo')
    search_fields = ('nombre', 'direccion')
    list_filter = ('tipo_establecimiento', 'nivel')
    inlines = [SucursalEspecialidadInline]

@admin.register(SucursalEspecialidad)
class SucursalEspecialidadAdmin(admin.ModelAdmin):
    list_display = ('sucursal', 'especialidad')
    list_filter = ('sucursal', 'especialidad')
