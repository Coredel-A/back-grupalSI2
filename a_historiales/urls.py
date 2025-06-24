from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (HistorialClinicoViewSet, DocumentoAdjuntoViewSet, 
                    FormularioViewSet, PreguntaViewSet, RespuestaViewSet,
                    DescargarDocumentoAPIView)

router = DefaultRouter()
router.register(r"historiales", HistorialClinicoViewSet, basename="historiales")
router.register(r"documentos", DocumentoAdjuntoViewSet, basename="documentos")
router.register(r"formularios", FormularioViewSet, basename="formularios")
router.register(r"preguntas", PreguntaViewSet, basename="preguntas")
router.register(r"respuestas", RespuestaViewSet, basename="respuestas")

urlpatterns = [
    path("", include(router.urls)),
    path('documentos/<uuid:documento_id>/descargar/', DescargarDocumentoAPIView.as_view(), name='descargar_documento'),
]