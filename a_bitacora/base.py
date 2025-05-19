from rest_framework import viewsets
from a_bitacora.utils import RegistroBitacora

class BitacoraModelViewSet(viewsets.ModelViewSet):
    bitacora_modulo = "General"

    def get_objeto_nombre(self, obj):
        for attr in ['nombre', 'titulo', 'name', 'title']:
            if hasattr(obj, attr):
                return getattr(obj, attr)
        return str(obj)

    def get_client_ip(self):
        return self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))

    def perform_create(self, serializer):
        obj = serializer.save()
        try:
            RegistroBitacora.registrar(
                usuario=self.request.user,
                accion=f"Creó {self.bitacora_modulo.lower()}: {self.get_objeto_nombre(obj)}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )
        except Exception as e:
            print(f"[Bitácora] Error al registrar creación: {e}")

    def perform_update(self, serializer):
        obj = serializer.save()
        try:
            RegistroBitacora.registrar(
                usuario=self.request.user,
                accion=f"Actualizó {self.bitacora_modulo.lower()}: {self.get_objeto_nombre(obj)}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )
        except Exception as e:
            print(f"[Bitácora] Error al registrar actualización: {e}")

    def perform_destroy(self, instance):
        nombre = self.get_objeto_nombre(instance)
        try:
            RegistroBitacora.registrar(
                usuario=self.request.user,
                accion=f"Eliminó {self.bitacora_modulo.lower()}: {nombre}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )
        except Exception as e:
            print(f"[Bitácora] Error al registrar eliminación: {e}")
        instance.delete()
