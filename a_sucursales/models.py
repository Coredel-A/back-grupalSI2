from django.db import models
from a_especialidades.models import Especialidad
import uuid

class Establecimiento(models.Model):
    TIPO_CHOICES = [
        ('hospital', 'Hospital'),
        ('clinica', 'Clínica'),
        ('consultorio', 'Consultorio'),
        ('centro_salud', 'Centro de Salud'),
        ('laboratorio', 'Laboratorio'),
        ('farmacia', 'Farmacia'),
    ]

    NIVEL_CHOICES = [
        ('nivel_1', 'Primer Nivel'),
        ('nivel_2', 'Segundo Nivel'),
        ('nivel_3', 'Tercer Nivel')
    ]

    nombre = models.CharField(max_length=100)
    direccion = models.TextField()
    telefono = models.CharField(max_length=100)
    correo = models.EmailField()
    tipo_establecimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    especialidades = models.ManyToManyField(Especialidad, through='SucursalEspecialidad')

    def __str__(self):
        return self.nombre
    
class SucursalEspecialidad(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, unique=True, default=uuid.uuid4)
    sucursal = models.ForeignKey(Establecimiento, on_delete=models.CASCADE)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sucursal', 'especialidad')
