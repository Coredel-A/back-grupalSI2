import json
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from a_roles.models import Rol

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, apellido, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(
            email=email,   
            nombre= nombre, 
            apellido = apellido,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        
        return self.create_user(email, nombre, apellido, password, **extra_fields)
    
class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(default=timezone.now)

    especialidad = models.ForeignKey('a_especialidades.Especialidad', on_delete=models.SET_NULL, null=True, blank=True)
    establecimiento = models.ForeignKey('a_sucursales.Establecimiento', on_delete=models.PROTECT, null=True, blank=True,)

    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def permisos_dict(self):
        permisos = {}
        if not self.rol:
            return permisos
        for permiso in self.rol.permisos.all():
            try:
                accion, modulo = permiso.codename.split('_', 1)
            except ValueError:
                continue
            if modulo not in permisos:
                permisos[modulo] = {}
            permisos[modulo][accion] = True
        return permisos


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"
    
