from django.shortcuts import render
from .models import Especialidad
from .serializers import EspecialidadSerializer
from rest_framework import viewsets

class EstablecimientoViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer

