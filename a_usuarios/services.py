from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Usuario
from .serializers import UsuarioSerializer
from a_bitacora.utils import RegistroBitacora


class UsuarioService:   
    @staticmethod
    def cambiar_password(usuario, nueva_password, usuario_solicitante):
        # Validar permisos
        if not (usuario_solicitante.is_superuser or usuario_solicitante == usuario):
            raise PermissionError("No tienes permisos para cambiar este password")
        
        # Validar contraseña
        if not nueva_password:
            raise ValueError("El password es obligatorio")
        
        if len(nueva_password) < 8:
            raise ValueError("El password debe tener al menos 8 caracteres")
        
        # Cambiar contraseña
        usuario.set_password(nueva_password)
        usuario.save()
    
    @staticmethod
    def asignar_grupo(usuario, group_id, usuario_solicitante):
        # Validar permisos
        if not usuario_solicitante.is_superuser:
            raise PermissionError("Solo los administradores pueden asignar grupos")
        
        # Validar group_id
        if not group_id:
            raise ValueError("El ID de grupo es obligatorio")
        
        # Asignar grupo
        group = Group.objects.get(id=group_id)
        usuario.groups.add(group)
        
        return group.name
    
    @staticmethod
    def remover_grupo(usuario, group_id, usuario_solicitante):
        # Validar permisos
        if not usuario_solicitante.is_superuser:
            raise PermissionError("Solo los administradores pueden remover grupos")
        
        # Validar group_id
        if not group_id:
            raise ValueError("El ID de grupo es obligatorio")
        
        # Remover grupo
        group = Group.objects.get(id=group_id)
        usuario.groups.remove(group)
        
        return group.name
    
    @staticmethod
    def asignar_permisos_grupo(group, permission_ids, usuario_solicitante):
        # Validar permisos
        if not usuario_solicitante.is_superuser:
            raise PermissionError("Solo los administradores pueden asignar permisos")
        
        # Validar permission_ids
        if not isinstance(permission_ids, list):
            raise ValueError("permission_ids debe ser una lista")
        
        # Obtener permisos
        permisos = Permission.objects.filter(id__in=permission_ids)
        
        if len(permisos) != len(permission_ids):
            raise ValueError("Algunos permisos no existen")
        
        # Asignar permisos
        group.permissions.set(permisos)
        
        return len(permisos)


class AuthService:
    @staticmethod
    def login(email, password, ip):
        # Validar datos requeridos
        if not email or not password:
            raise ValueError("Se requiere email y password")
        
        # Autenticar usuario
        user = authenticate(email=email, password=password)
        
        if not user:
            # Registrar intento fallido
            RegistroBitacora.registrar(
                usuario=None,
                accion=f"Intento de login fallido para email: {email}",
                ip=ip,
                modulo="Autenticación"
            )
            raise PermissionError("Credenciales inválidas")
        
        # Verificar que la cuenta esté activa
        if not user.is_active:
            raise PermissionError("La cuenta está desactivada")
        
        # Generar tokens
        refresh = RefreshToken.for_user(user)
        user_serializer = UsuarioSerializer(user)
        
        # Registrar login exitoso
        RegistroBitacora.registrar(
            usuario=user,
            accion="Inicio de sesión",
            ip=ip,
            modulo="Autenticación"
        )
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_serializer.data
        }
    
    @staticmethod
    @transaction.atomic
    def register(data, ip):
        # Validar datos
        serializer = UsuarioSerializer(data=data)
        if not serializer.is_valid():
            raise ValueError(str(serializer.errors))
        
        password = data.get('password')
        if not password:
            raise ValueError("El password es obligatorio")
        
        if len(password) < 8:
            raise ValueError("El password debe tener al menos 8 caracteres")
        
        # Crear usuario
        usuario = serializer.save()
        usuario.set_password(password)
        usuario.is_staff = False
        usuario.save()
        
        # Generar tokens
        refresh = RefreshToken.for_user(usuario)
        
        # Registrar en bitácora
        RegistroBitacora.registrar(
            usuario=usuario,
            accion="Auto-registro en el sistema",
            ip=ip,
            modulo="Autenticación"
        )
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serializer.data
        }
    
    @staticmethod
    def logout(refresh_token, usuario, ip):
        # Validar token
        if not refresh_token:
            raise ValueError("Se requiere el refresh token")
        
        try:
            # Registrar logout
            RegistroBitacora.registrar(
                usuario=usuario,
                accion="Cierre de sesión",
                ip=ip,
                modulo="Autenticación"
            )
            
            # Invalidar token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
        except Exception as e:
            raise ValueError("Error al cerrar sesión")


class PasswordService:
    @staticmethod
    def validar_fortaleza(password):
        errores = []
        
        if len(password) < 8:
            errores.append("Debe tener al menos 8 caracteres")
        
        if not any(c.isupper() for c in password):
            errores.append("Debe contener al menos una mayúscula")
        
        if not any(c.islower() for c in password):
            errores.append("Debe contener al menos una minúscula")
        
        if not any(c.isdigit() for c in password):
            errores.append("Debe contener al menos un número")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def generar_password_temporal():
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(12))
        return password