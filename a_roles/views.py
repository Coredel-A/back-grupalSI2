from django.shortcuts import render
from rest_framework import viewsets
from .models import Rol, Permiso
from .serializers import RolSerializer, RolWriteSerializer, PermisoSerializer
from a_usuarios.permissions import PermisosMixin
from a_bitacora.base import BitacoraModelViewSet

class PermisoViewSet(BitacoraModelViewSet, PermisosMixin):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    bitacora_modulo = "permisos"
    modulo_permisos = "permisos"

class RolViewSet(BitacoraModelViewSet, PermisosMixin):
    queryset = Rol.objects.all()
    bitacora_modulo = "roles"
    modulo_permisos = "roles"
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RolWriteSerializer
        return RolSerializer
    

