from django.db import models
import uuid

from django.forms import ValidationError

class Pacientes(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_nacimiento = models.DateField()

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

    residencia = models.CharField(max_length=100, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    ocupacion = models.CharField(max_length=100, blank=True, null=True)

    asegurado = models.BooleanField(default=False)
    beneficiario_de = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='beneficiarios'
    )

    def clean(self):
        if self.asegurado and self.beneficiario_de:
            raise ValidationError("Un paciente no puede ser asegurado y beneficiario al mismo tiempo.")

        if not self.asegurado and not self.beneficiario_de:
            raise ValidationError("Debe indicar un asegurado si el paciente no está asegurado.")

        if self.beneficiario_de and not self.beneficiario_de.asegurado:
            raise ValidationError("El paciente asociado como asegurador debe estar asegurado.")

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - CI: {self.ci}"
    

