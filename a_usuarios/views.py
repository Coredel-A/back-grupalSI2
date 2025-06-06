from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework_simplejwt.tokens import RefreshToken

from django_filters import rest_framework as filters
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, Permission
from django.db import transaction

from .models import Usuario
from .serializers import UsuarioSerializer, GroupSerializer, PermissionSerializer
from .permissions import PermisosMixin

from a_bitacora.utils import RegistroBitacora
from a_bitacora.decorators import registrar_accion

class UsuarioPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UsuarioFilter(filters.FilterSet):
    # Filtros básicos por campo exacto
    nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    apellido = filters.CharFilter(field_name='apellido', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    
    # Filtros por relaciones
    rol = filters.NumberFilter(field_name='rol__id')
    especialidad = filters.NumberFilter(field_name='especialidad__id')
    establecimiento = filters.NumberFilter(field_name='establecimiento__id')
    
    # Filtros de fecha
    fecha_nacimiento_after = filters.DateFilter(field_name='fecha_nacimiento', lookup_expr='gte')
    fecha_nacimiento_before = filters.DateFilter(field_name='fecha_nacimiento', lookup_expr='lte')
    
    # Filtro de estado
    is_active = filters.BooleanFilter(field_name='is_active')
    
    # Búsqueda general
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'email', 'rol', 'especialidad', 
            'establecimiento', 'is_active', 'fecha_nacimiento_after', 
            'fecha_nacimiento_before', 'search'
        ]
    
    def filter_search(self, queryset, name, value):
        """Filtro de búsqueda general en múltiples campos"""
        if value:
            return queryset.filter(
                Q(nombre__icontains=value) |
                Q(apellido__icontains=value) |
                Q(email__icontains=value)
            )
        return queryset


class UsuarioViewSet(PermisosMixin, viewsets.ModelViewSet):
    queryset = Usuario.objects.select_related('rol', 'especialidad', 'establecimiento').all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UsuarioPagination
    filterset_class = UsuarioFilter
    modulo_permisos = "usuario"
    search_fields = ['nombre', 'apellido', 'email']
    ordering_fields = ['nombre', 'apellido', 'email', 'fecha_registro']
    ordering = ['-fecha_registro']

    def get_queryset(self):
        """Optimizar consultas con select_related y prefetch_related"""
        return Usuario.objects.select_related(
            'rol', 'especialidad', 'establecimiento'
        ).prefetch_related(
            'rol__permisos'
        ).all()
    
    def list(self, request, *args, **kwargs):
        """Override list para añadir información adicional"""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        if not request.user.has_perm('a_usuarios.add_usuario'):
            return Response(
                {"error": "No tienes permisos para crear usuarios"},
                status=status.HTTP_403_FORBIDDEN
            )
            
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

        ip = self._get_client_ip(request)
        RegistroBitacora.registrar(
            usuario=request.user,
            accion=f"Creó usuario: {usuario.email}",
            ip=ip
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        if not self.request.user.has_perm('a_usuarios.change_usuario'):
            raise PermissionError("No tienes permisos para actualizar usuarios")
            
        usuario = serializer.save()
        ip = self._get_client_ip(self.request)
        RegistroBitacora.registrar(
            usuario=self.request.user,
            accion=f"Actualizó usuario: {usuario.email}",
            ip=ip
        )

    def perform_destroy(self, instance):
        if not self.request.user.has_perm('a_usuarios.delete_usuario'):
            raise PermissionError("No tienes permisos para eliminar usuarios")
            
        if instance == self.request.user:
            raise PermissionError("No puedes eliminarte a ti mismo")
            
        email = instance.email
        ip = self._get_client_ip(self.request)
        instance.delete()
        RegistroBitacora.registrar(
            usuario=self.request.user,
            accion=f"Eliminó usuario: {email}",
            ip=ip
        )

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        usuario = self.get_object()
        
        if not (request.user.is_superuser or request.user == usuario):
            return Response(
                {"error": "No tienes permisos para cambiar este password"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        password = request.data.get('password')
        if not password:
            return Response(
                {"error": "El password es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 8:
            return Response(
                {"error": "El password debe tener al menos 8 caracteres"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        usuario.set_password(password)
        usuario.save()
        
        ip = self._get_client_ip(request)
        RegistroBitacora.registrar(
            usuario=request.user,
            accion=f"Cambió password del usuario {usuario.email}",
            ip=ip
        )
        
        return Response({"message": "Password actualizado correctamente"})
    
    @action(detail=True, methods=['post'])
    def assign_group(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden asignar grupos"},
                status=status.HTTP_403_FORBIDDEN
            )

        usuario = self.get_object()
        group_id = request.data.get('group_id')

        if not group_id:
            return Response(
                {"error": "El ID de grupo es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            group = Group.objects.get(id=group_id)
            usuario.groups.add(group)

            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Asignó usuario {usuario.email} al grupo {group.name}",
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

    @action(detail=True, methods=['delete'])
    def remove_group(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden remover grupos"},
                status=status.HTTP_403_FORBIDDEN
            )

        usuario = self.get_object()
        group_id = request.data.get('group_id')

        if not group_id:
            return Response(
                {"error": "El ID de grupo es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            group = Group.objects.get(id=group_id)
            usuario.groups.remove(group)

            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Removió usuario {usuario.email} del grupo {group.name}",
                ip=ip
            )
            return Response(
                {"message": f"Usuario removido del grupo {group.name}"}
            )
        except Group.DoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_client_ip(self, request):
        """Método auxiliar para obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Group.objects.all()
        return Group.objects.none()

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden crear grupos"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        response = super().create(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_201_CREATED:
            ip = self._get_client_ip(request)
            group_name = response.data.get('name', 'Desconocido')
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Creó grupo: {group_name}",
                ip=ip
            )
        
        return response

    def update(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden actualizar grupos"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        instance = self.get_object()
        old_name = instance.name
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_200_OK:
            ip = self._get_client_ip(request)
            new_name = response.data.get('name', 'Desconocido')
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Actualizó grupo: {old_name} -> {new_name}",
                ip=ip
            )
        
        return response

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden eliminar grupos"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        instance = self.get_object()
        group_name = instance.name
        response = super().destroy(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Eliminó grupo: {group_name}",
                ip=ip
            )
        
        return response
    
    @action(detail=True, methods=['post'])
    def set_permissions(self, request, pk=None):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden asignar permisos"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        group = self.get_object()
        permission_ids = request.data.get('permission_ids', [])

        if not isinstance(permission_ids, list):
            return Response(
                {"error": "permission_ids debe ser una lista"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            permisos = Permission.objects.filter(id__in=permission_ids)
            
            if len(permisos) != len(permission_ids):
                return Response(
                    {"error": "Algunos permisos no existen"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            group.permissions.set(permisos)

            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Asignó {len(permisos)} permisos al grupo {group.name}",
                ip=ip
            )

            return Response({'message': 'Permisos asignados correctamente'})
            
        except Exception as e:
            return Response(
                {"error": "Error al asignar permisos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_client_ip(self, request):
        """Método auxiliar para obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PermissionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response(
                {"error": "Solo los administradores pueden ver los permisos"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        permisos = Permission.objects.all().order_by('content_type__app_label', 'codename')
        serializer = PermissionSerializer(permisos, many=True)
        return Response(serializer.data)


class MisPermisosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permisos = request.user.get_all_permissions()
        return Response({'permisos': list(permisos)})


class MisPermisosEstructuradosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        permisos_crudos = request.user.get_all_permissions()
        permisos_estructurados = {}

        for permiso in permisos_crudos:
            try:
                app_label, codename = permiso.split('.')
                accion, modelo = codename.split('_', 1)

                if modelo not in permisos_estructurados:
                    permisos_estructurados[modelo] = {
                        'view': False,
                        'add': False,
                        'change': False,
                        'delete': False
                    }
                
                if accion in permisos_estructurados[modelo]:
                    permisos_estructurados[modelo][accion] = True
            
            except ValueError:
                continue
        
        return Response(permisos_estructurados)


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
            if not user.is_active:
                return Response(
                    {"error": "La cuenta está desactivada"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
            refresh = RefreshToken.for_user(user)
            user_serializer = UsuarioSerializer(user)

            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=user,
                accion="Inicio de sesión",
                ip=ip
            )
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data
            })
        else:
            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=None,
                accion=f"Intento de login fallido para email: {email}",
                ip=ip
            )
            
            return Response(
                {"error": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def _get_client_ip(self, request):
        """Método auxiliar para obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


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
            
            if len(password) < 8:
                return Response(
                    {"error": "El password debe tener al menos 8 caracteres"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            usuario = serializer.save()
            usuario.set_password(password)
            usuario.is_staff = False
            usuario.save()

            refresh = RefreshToken.for_user(usuario)

            ip = self._get_client_ip(request)
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

    def _get_client_ip(self, request):
        """Método auxiliar para obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response(
                    {"error": "Se requiere el refresh token"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ip = self._get_client_ip(request)
            RegistroBitacora.registrar(
                usuario=request.user,
                accion="Cierre de sesión",
                ip=ip
            )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                "message": "Sesión cerrada correctamente"
            })
            
        except Exception as e:
            return Response(
                {"error": "Error al cerrar sesión"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_client_ip(self, request):
        """Método auxiliar para obtener la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip