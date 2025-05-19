from functools import wraps
from .models import Bitacora

def registrar_accion(descripcion=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            if request.user.is_authenticated:
                try:
                    accion_desc = descripcion
                    if descripcion and kwargs:
                        accion_desc = descripcion.format(**kwargs)

                    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                    if x_forwarded_for:
                        ip = x_forwarded_for.split(',')[0]
                    else:
                        ip = request.META.get('REMOTE_ADDR')

                    Bitacora.objects.create(
                        usuario=request.user,
                        accion=accion_desc or f"{request.method} en {request.path}",
                        ip=ip
                    )
                except Exception as e:
                    print(f"Error al registrar en bitacora: {e}")
            return response
        return wrapped_view
    return decorator

        