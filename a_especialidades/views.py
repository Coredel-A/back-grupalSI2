from rest_framework import permissions
from .models import Especialidad
from .serializers import EspecialidadSerializer
from a_bitacora.base import BitacoraModelViewSet

class EspecialidadViewSet(BitacoraModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [permissions.IsAuthenticated]
    bitacora_modulo = "Especialidad"

