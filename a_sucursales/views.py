from django.shortcuts import render
from .models import Establecimiento, SucursalEspecialidad
from .serializers import EstablecimientoSerializer, SucursalEspecialidadSerializer
from .filters import EstablecimientoFilter
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from a_bitacora.base import BitacoraModelViewSet
from a_usuarios.permissions import PermisosMixin

class EstablecimientoViewSet(PermisosMixin, BitacoraModelViewSet):
    queryset = Establecimiento.objects.all()
    serializer_class = EstablecimientoSerializer
    filterset_class = EstablecimientoFilter
    permission_classes= [IsAuthenticated]
    bitacora_modulo = "establecimiento"
    modulo_permisos = "establecimiento"
    

class SucursalEspecialidadViewSet(PermisosMixin, BitacoraModelViewSet):
    queryset = SucursalEspecialidad.objects.all()
    serializer_class = SucursalEspecialidadSerializer
    permission_classes = [IsAuthenticated]
    bitacora_modulo = "sucursal-especialidad"
    modulo_permisos = "sucursal-especialidad"