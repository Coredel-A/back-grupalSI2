from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import Usuario
from a_sucursales.models import Establecimiento
from a_especialidades.models import Especialidad
from a_sucursales.serializers import EstablecimientoSerializer
from a_especialidades.serializers import EspecialidadSerializer

class UsuarioSerializer(serializers.ModelSerializer):
    grupos = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        source='groups',
        required=False
    )

    especialidad = EspecialidadSerializer(read_only=True)
    establecimiento = EstablecimientoSerializer(read_only=True)

    especialidad_id = serializers.PrimaryKeyRelatedField(
        queryset=Especialidad.objects.all(), 
        source='especialidad', 
        write_only=True,
        required=False,
        allow_null=True
    )
    establecimiento_id = serializers.PrimaryKeyRelatedField(
        queryset=Establecimiento.objects.all(), 
        source='establecimiento', 
        write_only=True,
    )

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre', 'apellido', 'email',
            'fecha_nacimiento', 'fecha_registro',
            'especialidad', 'especialidad_id',
            'establecimiento', 'establecimiento_id',
            'grupos', 'is_active', 'is_staff', 'password'
        ]

        read_only_fields = ['fecha_registro']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', [])

        user = Usuario.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.save()
        
        if groups:
            user.groups.set(groups)

        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        groups = validated_data.pop('groups', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if groups is not None:
            instance.groups.set(groups)

        return instance

