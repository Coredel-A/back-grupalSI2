from django.http import HttpResponseForbidden

def permiso_requerido(codename):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated and user.rol and user.rol.permisos.filter(codename=codename).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permiso.")
        return _wrapped_view
    return decorator
