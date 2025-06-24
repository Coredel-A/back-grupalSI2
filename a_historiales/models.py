from django.db import models
import uuid
from a_usuarios.models import Usuario
from a_pacientes.models import Pacientes
from a_sucursales.models import Especialidad

class Formulario(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=255)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Pregunta(models.Model):
    TIPO_DATO_CHOICES = [
        ('texto', 'Texto'),
        ('numero', 'Numero'),
        ('booleano', 'Booleano'),
        ('fecha', 'Fecha'),
        ('textarea', 'Texto largo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formulario = models.ForeignKey(Formulario, on_delete=models.CASCADE, related_name='preguntas')
    texto = models.TextField()
    tipo_dato = models.CharField(max_length=20, choices=TIPO_DATO_CHOICES)
    obligatorio = models.BooleanField(default=False)
    orden = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.texto} ({self.tipo_dato})"

class HistorialClinico(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.ForeignKey(Pacientes, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)
    formulario = models.ForeignKey(Formulario, null=True, blank=True, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    motivo_consulta = models.TextField()
    fuente = models.CharField(max_length=255)
    confiabilidad = models.CharField(max_length=225, null=True, blank=True)
    diagnostico = models.TextField()
    signos_vitales = models.JSONField()

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial Clinico'
        verbose_name_plural = 'Historiales Clinicos'

    def __str__(self):
        return f"{self.paciente} - {self.fecha}"
    
class Respuesta(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    historial_clinico = models.ForeignKey(HistorialClinico, on_delete=models.CASCADE, null=True, blank=True)
    valor = models.TextField()

    def __str__(self):
        return f"Respuesta a:{self.pregunta.texto}"
    
class DocumentoAdjunto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historial = models.ForeignKey(HistorialClinico, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=255)
    archivo = models.FileField()
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_documento} - {self.fecha_subida}"