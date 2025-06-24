from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from .models import HistorialClinico, Formulario, Pregunta, Respuesta, DocumentoAdjunto
from .serializers import (
    HistorialClinicoSerializer, FormularioSerializer, PreguntaSerializer, 
    RespuestaSerializer, DocumentoAdjuntoSerializer, PreguntaConRespuestaSerializer)
from a_bitacora.base import BitacoraModelViewSet

class HistorialClinicoViewSet(BitacoraModelViewSet):
    queryset = HistorialClinico.objects.all()
    serializer_class = HistorialClinicoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['motivo_consulta', 'diagnostico', 'fuente', 'confiabilidad']
    filterset_fields = ['paciente', 'usuario', 'especialidad', 'fecha']
    ordering_fields = ['fecha']
    ordering = ['-fecha']

    @action(detail=True, methods=['get'], url_path='formulario-completo')
    def formulario_completo(self, request, pk=None):
        try:
            # Obtener la instancia del historial clínico
            historia = self.get_object()
            
            # Verificar que se ha obtenido la historia correctamente
            if not historia:
                return Response({'detail': 'Historial Clínico no encontrado'}, status=404)

            # Acceder a la especialidad
            especialidad = historia.especialidad
            if not especialidad:
                return Response({'detail': 'Especialidad no encontrada en el historial clínico'}, status=404)

            # Obtener formulario relacionado con la especialidad
            formulario = Formulario.objects.filter(especialidad=especialidad, activo=True).first()
            if not formulario:
                return Response({'detail': 'No hay formulario asociado'}, status=404)

            # Obtener preguntas relacionadas con el formulario
            preguntas = Pregunta.objects.filter(formulario=formulario).order_by('orden')
            if not preguntas:
                return Response({'detail': 'No hay preguntas asociadas al formulario'}, status=404)

            # Pasar el historial_clinico al contexto para que las respuestas puedan ser recuperadas correctamente
            serializer = PreguntaConRespuestaSerializer(preguntas, many=True, context={'historial_clinico': historia})

            return Response({
                'formulario': FormularioSerializer(formulario).data,
                'preguntas_respuestas': serializer.data
            })

        except HistorialClinico.DoesNotExist:
            return Response({'detail': 'Historial Clínico no encontrado'}, status=404)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)

    @action(detail=True, methods=['patch'], url_path='asignar-formulario')
    def asignar_formulario(self, request, pk=None):
        try:
            historial = self.get_object()  # Obtener historial clínico
            formulario_id = request.data.get('formulario')

            if not formulario_id:
                return Response({'detail': 'Formulario no proporcionado'}, status=400)

            # Obtener el formulario
            try:
                formulario = Formulario.objects.get(id=formulario_id)
            except Formulario.DoesNotExist:
                return Response({'detail': 'Formulario no encontrado'}, status=404)

            # Asignar formulario al historial
            historial.formulario = formulario
            historial.save()

            # Procesar las respuestas enviadas
            respuestas_data = request.data.get('respuestas', [])
            
            for respuesta_item in respuestas_data:
                pregunta_id = respuesta_item.get('pregunta')
                valor = respuesta_item.get('valor')

                if not pregunta_id:
                    continue

                try:
                    pregunta = Pregunta.objects.get(id=pregunta_id)
                except Pregunta.DoesNotExist:
                    continue

                # Buscar si ya existe una respuesta para esta pregunta y historial
                respuesta_existente = Respuesta.objects.filter(
                    pregunta=pregunta, 
                    historial_clinico=historial
                ).first()

                if respuesta_existente:
                    # Actualizar respuesta existente
                    respuesta_existente.valor = valor
                    respuesta_existente.save()
                else:
                    # Crear nueva respuesta
                    Respuesta.objects.create(
                        pregunta=pregunta,
                        historial_clinico=historial,
                        valor=valor
                    )

            # Serializar el historial actualizado
            historial_serializado = HistorialClinicoSerializer(historial).data

            return Response({
                'detail': 'Formulario y respuestas asignadas correctamente',
                'historial': historial_serializado
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'detail': f'Error interno: {str(e)}'}, status=500)

    
    @action(detail=True, methods=['get'], url_path='formularios-especialidad')
    def formularios_por_especialidad(self, request, pk=None):
        try:
            # Obtener la historia clínica
            historia = self.get_object()
            especialidad_id = historia.especialidad.id

            # Obtener formularios asociados a la especialidad
            formularios = Formulario.objects.filter(especialidad=especialidad_id, activo=True)
            serializer = FormularioSerializer(formularios, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'detail': f'Error al obtener formularios: {str(e)}'}, status=500)

class FormularioViewSet(BitacoraModelViewSet):
    queryset = Formulario.objects.all()
    serializer_class = FormularioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'especialidad', 'activo']
    ordering_fields = ['nombre']
    ordering = ['nombre']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtrar por nombre si el parámetro 'nombre' está presente
        nombre = self.request.query_params.get('nombre', None)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)

        # Filtrar por especialidad si el parámetro 'especialidad' está presente
        especialidad = self.request.query_params.get('especialidad', None)
        if especialidad:
            queryset = queryset.filter(especialidad=especialidad)

        # Filtrar por estado activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            # Asegúrate de manejar correctamente el valor de "activo"
            queryset = queryset.filter(activo=(activo.lower() == 'true'))

        return queryset

class PreguntaViewSet(BitacoraModelViewSet):
    queryset = Pregunta.objects.all()
    serializer_class = PreguntaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['formulario']
    ordering_fields = ['orden']
    ordering = ['orden']

    def create(self, request, *args, **kwargs):
        # Verifica si estamos enviando una lista de preguntas
        if isinstance(request.data, list):
            # Si es una lista, procesamos las preguntas individualmente
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            # Si solo es una pregunta, procesamos un solo objeto
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RespuestaViewSet(BitacoraModelViewSet):
    queryset = Respuesta.objects.all()
    serializer_class = RespuestaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pregunta', 'historial_clinico']

class DocumentoAdjuntoViewSet(BitacoraModelViewSet):
    queryset = DocumentoAdjunto.objects.all()
    serializer_class = DocumentoAdjuntoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['historial', 'tipo_documento', 'fecha_subida']
    parser_classes = (MultiPartParser, FormParser)
    ordering_fields = ['fecha_subida']
    ordering = ['-fecha_subida']

class AdjuntarDocumentoAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        archivo = request.FILES.get('archivo')
        tipo_documento = request.data.get('tipo_documento')
        historial_id = request.data.get('historial')

        if not archivo or not historial_id:
            return Response({"error": "Archivo o historial no proporcionados"}, status=400)

        historial = HistorialClinico.objects.get(id=historial_id)
        documento = DocumentoAdjunto.objects.create(
            historial=historial,
            tipo_documento=tipo_documento,
            archivo=archivo
        )

        return Response({'message': 'Documento adjuntado exitosamente'}, status=201)
    
class DescargarDocumentoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, documento_id):
        try:
            # Obtener el documento adjunto
            documento = DocumentoAdjunto.objects.get(id=documento_id)
            file_path = documento.archivo.path
            file_name = documento.archivo.name.split("/")[-1]  # Obtener solo el nombre del archivo

            # Verificar si el archivo existe
            if not documento.archivo:
                return Response({'detail': 'Archivo no encontrado'}, status=404)

            # Usar FileResponse para devolver el archivo
            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
            response['Content-Type'] = 'application/octet-stream'  # Asegurar tipo binario
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'  # Forzar descarga

            return response

        except DocumentoAdjunto.DoesNotExist:
            return Response({'detail': 'Documento no encontrado'}, status=404)

