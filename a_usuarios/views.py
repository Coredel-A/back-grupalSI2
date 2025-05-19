from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.db import transaction

from .models import Usuario
from .serializers import UsuarioSerializer

from a_bitacora.utils import RegistroBitacora
from a_bitacora.decorators import registrar_accion

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Usuario.objects.all()
        return Usuario.objects.filter(pk=user.pk)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password = request.data.get('password')
        if not password:
            return Response(
                {"error": "El password es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario = serializer.save()
        usuario.set_password(password)
        usuario.save()

        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        RegistroBitacora.registrar(
            usuario=request.user,
            accion=f"Creo usuario: {usuario.email}",
            ip=ip
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        usuario = serializer.save()
        ip = self.META.get('HTTP_X_FORWARDED_FOR', self.META.get('REMOTE_ADDR'))
        RegistroBitacora.registrar(
            usuario=self.request.user,
            accion=f"Actualizo usuario: {usuario.email}",
            ip=ip
        )

    def perform_destroy(self, instance):
        email = instance.email
        ip = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR'))
        instance.delete()
        RegistroBitacora.registrar(
            usuario=self.request.user,
            accion=f"Elimino usuario: {email}",
            ip=ip
        )

    @action(detail=True, methods=['post'])
    @registrar_accion("Cambio password del usuari {pk}")
    def set_password(self, request, pk=None):
        usuairo = self.get_object()
        password = request.data.get('password')

        if not password:
            return Response(
                {"error": "El password es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuairo.set_password(password)
        usuairo.save()
        return Response({"message": "password actualizado correctamente"})
    
    @action(detail=True, methods=['post'])
    @registrar_accion("Asigno grupo al usuario {pk}")
    def assign_group(self, request, pk=None):

        usuario = self.get_object()
        group_id = request.data.get('group_id')

        if not group_id:
            return Response(
                {"error": "ID de gruop es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            group = Group.objects.get(id=group_id)
            usuario.groups.add(group)

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Asigno usuario {usuario.email} al grupo {group.name}",
                ip=ip
            )
            return Response(
                {"message": f"Usuario asignado al grupo {group.name}"}
            )
        except Group.DoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Se requiere email y password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            user_serializer = UsuarioSerializer(user)

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            RegistroBitacora.registrar(
                usuario=user,
                accion=f"Inicio de sesion",
                ip=ip
            )
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            })
        else:
            return Response(
                {"error": "Credenciales invalidad"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)

        if serializer.is_valid():
            password = request.data.get('password')

            if not password:
                return Response(
                    {"error": "El password es obligatorio"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            usuario = serializer.save()
            usuario.set_password(password)
            usuario.is_staff = False
            usuario.save()

            refresh = RefreshToken.for_user(usuario)

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            RegistroBitacora.registrar(
                usuario=usuario,
                accion="Auto-registro en el sistema",
                ip=ip
            )
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            RegistroBitacora.registrar(
                usuario=request.user,
                accion="Cierre de sesion",
                ip=ip
            )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                "message": "Sesion cerrada correctamente"
            })
        except Exception:
            return Response(
                {"error": "Error al cerrar sesion"},
                status=status.HTTP_400_BAD_REQUEST
            )
    