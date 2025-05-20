from rest_framework import serializers
from .models import Pacientes

class BeneficiarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pacientes
        fields = ['id', 'nombre', 'apellido']

class PacientesSerializer(serializers.ModelSerializer):
    beneficiario_de = BeneficiarioSerializer(read_only=True)
    beneficiario_de_id = serializers.PrimaryKeyRelatedField(
        queryset = Pacientes.objects.all(), source = 'beneficiario_de', write_only=True, required=False
    )

    class Meta:
        model = Pacientes
        fields = [
            'id', 'nombre', 'apellido', 'ci', 'telefono', 'email',
            'fecha_nacimiento', 'sexo', 'residencia', 'direccion',
            'religion', 'ocupacion', 'asegurado',
            'beneficiario_de', 'beneficiario_de_id'
        ]