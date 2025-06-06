from django.shortcuts import render
from rest_framework import viewsets
from .models import Rol, Permiso
from .serializers import RolSerializer, RolWriteSerializer, PermisoSerializer

class PermisoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RolWriteSerializer
        return RolSerializer
    

