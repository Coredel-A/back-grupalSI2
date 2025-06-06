from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from .models import Usuario
from a_roles.models import Rol, Permiso
from a_sucursales.models import Establecimiento
from a_especialidades.models import Especialidad
from a_sucursales.serializers import EstablecimientoSerializer
from a_especialidades.serializers import EspecialidadSerializer

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre']

class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        source='rol',
        write_only=True,
        required=False,
        allow_null=True,
    )
    
    especialidad = EspecialidadSerializer(read_only=True)
    especialidad_id = serializers.PrimaryKeyRelatedField(
        queryset=Especialidad.objects.all(), 
        source='especialidad', 
        write_only=True,
        required=False,
        allow_null=True
    )
    
    establecimiento = EstablecimientoSerializer(read_only=True)
    establecimiento_id = serializers.PrimaryKeyRelatedField(
        queryset=Establecimiento.objects.all(), 
        source='establecimiento', 
        write_only=True,
    )

    password = serializers.CharField(write_only=True, required=False)

    permisos = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre', 'apellido', 'email',
            'fecha_nacimiento', 'fecha_registro',
            'especialidad', 'especialidad_id',
            'establecimiento', 'establecimiento_id',
            'rol', 'rol_id', 'permisos', 'is_active', 'is_staff', 'password'
        ]
        read_only_fields = ['fecha_registro']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

    def get_permisos(self, user):
        if user.rol:
            return list(user.rol.permisos.values_list('codename', flat=True))
        return []

    
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name']
    
class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

