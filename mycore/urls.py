from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('a_usuarios.urls')),
    path('api/sucursales/', include('a_sucursales.urls')),
    path('api/especialidades/', include('a_especialidades.urls')),
    path('api/bitacora/', include('a_bitacora.urls')),
    path('api/pacientes/', include('a_pacientes.urls')),
]
