from rest_framework import serializers
from .models import Establecimiento, SucursalEspecialidad
from a_especialidades.models import Especialidad
from a_especialidades.serializers import EspecialidadSerializer

class EstablecimientoSerializer(serializers.ModelSerializer):
    especialidades = EspecialidadSerializer(
        many=True,
        read_only=True
    )

    especialidades_ids = serializers.PrimaryKeyRelatedField(
        queryset=Especialidad.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    tipo_establecimiento_display = serializers.SerializerMethodField()
    nivel_display = serializers.SerializerMethodField()

    class Meta:
        model = Establecimiento
        fields = ['id', 'nombre', 'direccion', 'telefono', 'correo',
                  'tipo_establecimiento', 'tipo_establecimiento_display',
                    'nivel','nivel_display', 'especialidades', 'especialidades_ids']

    def get_tipo_establecimiento_display(self, obj):
        return obj.get_tipo_establecimiento_display()

    def get_nivel_display(self, obj):
        return obj.get_nivel_display()

    def create(self, validated_data):
        especialidades = validated_data.pop('especialidades_ids', [])
        establecimiento = Establecimiento.objects.create(**validated_data)

        for especialidad in especialidades:
            SucursalEspecialidad.objects.create(
                sucursal=establecimiento,
                especialidad=especialidad
            )     
        
        return establecimiento
    
    def update(self, instance, validated_data):
        especialidades = validated_data.pop('especialidades_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if especialidades is not None:
            SucursalEspecialidad.objects.filter(sucursal=instance).delete()

            for especialidad in especialidades:
                SucursalEspecialidad.objects.create(
                    sucursal=instance,
                    especialidad=especialidad
                )
        return instance
    
class SucursalEspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SucursalEspecialidad
        fields = '__all__'

