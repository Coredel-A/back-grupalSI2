from rest_framework import serializers
from .models import Rol, Permiso

class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = ['id', 'codename', 'descripcion']

class RolSerializer(serializers.ModelSerializer):
    permisos = PermisoSerializer(many=True, read_only=True)

    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'permisos']

# Para crear/editar roles con permisos (POST/PUT)
class RolWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'permisos']
