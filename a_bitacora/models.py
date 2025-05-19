from django.db import models
from django.utils import timezone
from a_usuarios.models import Usuario
import uuid

class Bitacora(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='acciones_bitacora')
    accion = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    ip = models.GenericIPAddressField()

    modulo = models.CharField(max_length=100, blank=True, null=True)
    detalles = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Entrada de bitacora'
        verbose_name_plural = 'Entradas de bitacora'

    def __str__(self):
        return f"{self.timestamp} - {self.usuario.email} - {self.accion}"
