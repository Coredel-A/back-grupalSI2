from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Pacientes
from .serializers import PacientesSerializer
from .filters import PacientesFilter
from a_bitacora.base import BitacoraModelViewSet
from a_usuarios.permissions import PermisosMixin

class PacientesViewSet(PermisosMixin, BitacoraModelViewSet):
    queryset = Pacientes.objects.all()
    serializer_class = PacientesSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['nombre', 'apellido', 'fecha_nacimiento']
    ordering = ['apellido']  # orden por defecto
    filterset_class = PacientesFilter
    permission_classes = [IsAuthenticated] 
    bitacora_modulo = "pacientes"
    modulo_permisos = "pacientes"

