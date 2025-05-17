from django.shortcuts import render
from .models import Establecimiento
from .serializers import EstablecimientoSerializer
from rest_framework import viewsets

class EstablecimientoViewSet(viewsets.ModelViewSet):
    queryset = Establecimiento.objects.all()
    serializer_class = EstablecimientoSerializer

