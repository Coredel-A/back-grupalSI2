from rest_framework import serializers
from .models import Bitacora
from a_usuarios.serializers import UsuarioSerializer

class BitacoraSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Bitacora
        fields = ['id', 'usuario', 'accion', 'timestamp', 'ip']
        read_only_fields = ['id', 'timestamp']