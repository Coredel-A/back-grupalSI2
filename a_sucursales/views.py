from django.shortcuts import render
from .models import Establecimiento
from .serializers import EstablecimientoSerializer
from rest_framework import viewsets
from a_bitacora.base import BitacoraModelViewSet

class EstablecimientoViewSet(BitacoraModelViewSet):
    queryset = Establecimiento.objects.all()
    serializer_class = EstablecimientoSerializer
    bitacora_modulo = "Establecimiento"

