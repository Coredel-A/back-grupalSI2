from rest_framework.exceptions import PermissionDenied

class PermisosMixin:
    modulo_permisos = None  # Debe ser sobrescrito en cada ViewSet, ej: "pacientes"

    def get_permisos_usuario(self):
        # Aquí usamos la nueva propiedad
        return getattr(self.request.user, "permisos_dict", {})

    def check_permiso(self, accion):
        permisos = self.get_permisos_usuario()
        print("Permisos del usuario:", permisos)
        tiene_permiso = permisos.get(self.modulo_permisos, {}).get(accion, False)
        if not tiene_permiso:
            mensaje = f"No tiene permiso para {self.get_mensaje_accion(accion)}"
            raise PermissionDenied(mensaje)
        return True

    def get_mensaje_accion(self, accion):
        mensajes = {
            "view": "ver este recurso.",
            "add": "agregar un nuevo registro.",
            "change": "editar este recurso.",
            "delete": "eliminar este recurso."
        }
        return mensajes.get(accion, "realizar esta acción.")

    def list(self, request, *args, **kwargs):
        self.request = request
        self.check_permiso("view")
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.request = request
        self.check_permiso("view")
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.request = request
        self.check_permiso("add")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.request = request
        self.check_permiso("change")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.request = request
        self.check_permiso("change")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.request = request
        self.check_permiso("delete")
        return super().destroy(request, *args, **kwargs)
