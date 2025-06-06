from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstablecimientoViewSet, SucursalEspecialidadViewSet

router = DefaultRouter()
router.register(r'establecimientos', EstablecimientoViewSet)
router.register(r'sucursal-especialidades', SucursalEspecialidadViewSet)

urlpatterns = [
    path('',include(router.urls)),
]