from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import HistorialClinico, Formulario, Pregunta, Respuesta, DocumentoAdjunto
from .serializers import (HistorialClinicoSerializer, FormularioSerializer, PreguntaSerializer, RespuestaSerializer, DocumentoAdjuntoSerializer,)
from a_bitacora.base import BitacoraModelViewSet

class HistorialClinicoViewSet(BitacoraModelViewSet):
    queryset = HistorialClinico.objects.all()
    serializer_class = HistorialClinicoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['motivo_consulta', 'diagnostico', 'fuente', 'confiabilidad']

    filterset_fields = ['paciente', 'usuario', 'especialidad', 'fecha']

    ordering_fields = ['fecha']
    ordering = ['-fecha']

class FormularioViewSet(BitacoraModelViewSet):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['especialidad', 'activo']
    ordering_fields = ['nombre']
    ordering = ['nombre']

class PreguntaViewSet(BitacoraModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['formulario']
    ordering_fields = ['orden']
    ordering = ['orden']

class RespuestaViewSet(BitacoraModelViewSet):
    queryset = Respuesta.objects.all()
    serializer_class = RespuestaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['historial', 'pregunta']

class DocumentoAdjuntoViewSet(BitacoraModelViewSet):
    queryset = DocumentoAdjunto.objects.all()
    serializer_class = DocumentoAdjuntoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['historial', 'tipo_documento', 'fecha_subida']
    ordering_fields = ['fecha_subida']
    ordering = ['-fecha_subida']