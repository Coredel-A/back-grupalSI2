from .models import Bitacora
from django.utils import timezone

class RegistroBitacora:
    @staticmethod
    def registrar(usuario, accion, ip=None, modulo=None, detalles=None):
        try:
            Bitacora.objects.create(
                usuario=usuario,
                accion=accion,
                ip=ip,
                modulo=modulo,
                detalles=detalles,
            )
            return True
        except Exception as e:
            print(f"Error al registrar en bitacora: {e}")
            return False