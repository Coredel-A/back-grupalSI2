from rest_framework import serializers
from .models import Establecimiento, SucursalEspecialidad
from a_especialidades.models import Especialidad

class EstablecimientoSerializer(serializers.ModelSerializer):
    especialidades = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    especialidades_ids = serializers.PrimaryKeyRelatedField(
        queryset=Especialidad.objects.all(),
        many=True,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Establecimiento
        fields = ['id', 'nombre', 'direccion', 'telefono', 'correo',
                  'tipo_establecimiento', 'nivel', 'especialidades', 'especialidades_ids']

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


