from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .models import Especialidad
from .serializers import EspecialidadSerializer
from a_bitacora.base import BitacoraModelViewSet
from a_usuarios.permissions import PermisosMixin

class EspecialidadViewSet(PermisosMixin, BitacoraModelViewSet):
    queryset = Especialidad.objects.all()
    serializer_class = EspecialidadSerializer
    permission_classes = [IsAuthenticated]
    bitacora_modulo = "especialidad"
    modulo_permisos = "especialidad"

