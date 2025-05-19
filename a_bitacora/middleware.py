from .models import Bitacora
from django.conf import settings
import re

class BitacoraMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.EXEMPT_URLS = [
            re.compile(settings.STATIC_URL),
            re.compile(r'^/admin/'),
        ]
        self.METHODS_TO_LOG = ['POST', 'PUT', 'PATCH', 'DELETE']

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        path = request.path_info
        if any(m.match(path) for m in self.EXEMPT_URLS):
            return None

        if request.method not in self.METHODS_TO_LOG:
            return None

        try:
            usuario = request.user
            accion = f"{request.method} en {path}"

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

            Bitacora.objects.create(
                usuario=usuario,
                accion=accion,
                ip=ip
            )
        except Exception as e:
            print(f"Error al registrar en bitácora: {e}")

        return None
