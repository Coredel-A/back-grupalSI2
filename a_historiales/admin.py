from django.contrib import admin
from .models import DocumentoAdjunto

class DocumentoAdjuntoAdmin(admin.ModelAdmin):
    list_display = ('tipo_documento', 'archivo', 'fecha_subida', 'historial')
    search_fields = ('tipo_documento', 'historial__paciente')
    list_filter = ('tipo_documento', 'fecha_subida')

admin.site.register(DocumentoAdjunto, DocumentoAdjuntoAdmin)
