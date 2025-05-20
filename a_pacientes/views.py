from rest_framework import viewsets, permissions
from .models import Pacientes
from .serializers import PacientesSerializer
from a_bitacora.base import BitacoraModelViewSet

class PacientesViewSet(BitacoraModelViewSet):
    queryset = Pacientes.objects.all()
    serializer_class = PacientesSerializer
    permission_classes = [permissions.IsAuthenticated]
    bitacora_modulo = "Paciente"
