from rest_framework import serializers
from .models import HistorialClinico, Formulario, Pregunta, Respuesta, DocumentoAdjunto

class DocumentoAdjuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoAdjunto
        fields = '__all__'

class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = '__all__'

class PreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pregunta
        fields = '__all__'

class FormularioSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True, source='pregunta_set')

    class Meta:
        model = Formulario
        fields = '__all__'

class HistorialClinicoSerializer(serializers.ModelSerializer):
    documento_adjunto =DocumentoAdjuntoSerializer(many=True, read_only=True, source='documentoadjunto_set')
    respuesta = RespuestaSerializer(many=True, read_only=True, source='respuesta_set')

    class Meta:
        model = HistorialClinico
        fields = '__all__'