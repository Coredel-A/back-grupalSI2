from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('a_usuarios.urls')),
    path('api/roles/', include('a_roles.urls')),
    path('api/sucursales/', include('a_sucursales.urls')),
    path('api/especialidades/', include('a_especialidades.urls')),
    path('api/bitacora/', include('a_bitacora.urls')),
    path('api/pacientes/', include('a_pacientes.urls')),
    path('api/historiales/', include('a_historiales.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
