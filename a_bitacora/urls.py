from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BitacoraViewSet, exportar_bitacora_pdf

router = DefaultRouter()
router.register(r'', BitacoraViewSet)

urlpatterns = [
    path('', include(router.urls)),
    #path('bitacora/exportar-pdf/', exportar_bitacora_pdf, name='exportar_bitacora_pdf'),
]