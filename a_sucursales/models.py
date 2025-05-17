from django.db import models

class Establecimiento(models.Model):
    TIPO_CHOICES = [
        ('hospital', 'Hospital'),
        ('clinica',' Clinica'),
        ('consultorio', 'Consultorio'),
        ('centroo_salud', 'Centro de Salud'),
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

    def __str__(self):
        return self.nombre
