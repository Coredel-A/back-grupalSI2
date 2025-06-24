from rest_framework import serializers
from .models import HistorialClinico, Formulario, Pregunta, Respuesta, DocumentoAdjunto

class DocumentoAdjuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoAdjunto
        fields = '__all__'

class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = ['id', 'pregunta', 'historial_clinico', 'valor']

class PreguntaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Pregunta
        fields = '__all__'

class PreguntaConRespuestaSerializer(serializers.ModelSerializer):
    respuesta = serializers.SerializerMethodField()

    class Meta:
        model = Pregunta
        fields = ['id', 'texto', 'tipo_dato', 'obligatorio', 'orden', 'respuesta']

    def get_respuesta(self, obj):
        # Recupera el historial clínico del contexto
        historial_clinico = self.context.get('historial_clinico')
        
        # Verifica que el historial clínico no sea None
        if historial_clinico:
            respuesta = Respuesta.objects.filter(pregunta=obj, historial_clinico=historial_clinico).first()
            return respuesta.valor if respuesta else None
        return None

class FormularioSerializer(serializers.ModelSerializer):
    preguntas = PreguntaConRespuestaSerializer(many=True, read_only=True)

    class Meta:
        model = Formulario
        fields = '__all__'

class HistorialClinicoSerializer(serializers.ModelSerializer):
    documento_adjunto = DocumentoAdjuntoSerializer(many=True, read_only=True, source='documentoadjunto_set')
    formulario = FormularioSerializer(read_only=True, required=False)  # Hacer que formulario sea opcional
    preguntas_respuestas = serializers.SerializerMethodField()  # Agregar un campo de preguntas_respuestas

    class Meta:
        model = HistorialClinico
        fields = '__all__'

    def get_preguntas_respuestas(self, obj):
        # Obtener el formulario asignado al historial
        formulario = obj.formulario
        if formulario:
            # Obtener las preguntas del formulario
            preguntas = Pregunta.objects.filter(formulario=formulario).order_by('orden')
            respuestas = []

            for pregunta in preguntas:
                # Buscar la respuesta asociada a cada pregunta en este historial clínico
                respuesta = Respuesta.objects.filter(pregunta=pregunta, historial_clinico=obj).first()
                respuestas.append({
                    'pregunta_id': pregunta.id,
                    'texto': pregunta.texto,
                    'tipo_dato': pregunta.tipo_dato,
                    'respuesta': respuesta.valor if respuesta else None
                })

            return respuestas
        return []   





