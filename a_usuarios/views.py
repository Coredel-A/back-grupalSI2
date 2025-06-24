from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
from .services import UsuarioService, AuthService

from a_bitacora.utils import RegistroBitacora
from a_bitacora.base import BitacoraModelViewSet


class UsuarioPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UsuarioFilter(filters.FilterSet):
    nombre = filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    apellido = filters.CharFilter(field_name='apellido', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    
    rol = filters.NumberFilter(field_name='rol__id')
    especialidad = filters.NumberFilter(field_name='especialidad__id')
    establecimiento = filters.NumberFilter(field_name='establecimiento__id')
    
    fecha_nacimiento_after = filters.DateFilter(field_name='fecha_nacimiento', lookup_expr='gte')
    fecha_nacimiento_before = filters.DateFilter(field_name='fecha_nacimiento', lookup_expr='lte')
    fecha_registro_after = filters.DateFilter(field_name='fecha_registro', lookup_expr='gte')
    fecha_registro_before = filters.DateFilter(field_name='fecha_registro', lookup_expr='lte')
    
    is_active = filters.BooleanFilter(field_name='is_active')
    is_staff = filters.BooleanFilter(field_name='is_staff')
    
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Usuario
        fields = [
            'nombre', 'apellido', 'email', 'rol', 'especialidad', 
            'establecimiento', 'is_active', 'is_staff',
            'fecha_nacimiento_after', 'fecha_nacimiento_before',
            'fecha_registro_after', 'fecha_registro_before', 'search'
        ]
    
    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(nombre__icontains=value) |
                Q(apellido__icontains=value) |
                Q(email__icontains=value) |
                Q(rol__nombre__icontains=value) |
                Q(especialidad__nombre__icontains=value) |
                Q(establecimiento__nombre__icontains=value)
            )
        return queryset


class UsuarioViewSet(PermisosMixin, BitacoraModelViewSet):
    queryset = Usuario.objects.select_related('rol', 'especialidad', 'establecimiento').all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UsuarioPagination
    filterset_class = UsuarioFilter
    bitacora_modulo = "usuario"
    modulo_permisos = "usuario"
    search_fields = ['nombre', 'apellido', 'email']
    ordering_fields = ['nombre', 'apellido', 'email', 'fecha_registro']
    ordering = ['-fecha_registro']

    def get_queryset(self):
        return Usuario.objects.select_related(
            'rol', 'especialidad', 'establecimiento'
        ).prefetch_related(
            'rol__permisos'
        ).all()

    def perform_create(self, serializer):
        password = self.request.data.get('password')
        if not password:
            raise ValueError("El password es obligatorio")
        
        usuario = serializer.save()
        usuario.set_password(password)
        usuario.save()
        return usuario

    def perform_destroy(self, instance):
        if instance == self.request.user:
            raise PermissionError("No puedes eliminarte a ti mismo")
        
        super().perform_destroy(instance)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        usuario = self.get_object()
        password = request.data.get('password')
        
        try:
            UsuarioService.cambiar_password(
                usuario=usuario,
                nueva_password=password,
                usuario_solicitante=request.user
            )
            
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Cambió password del usuario {usuario.email}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )
            
            return Response({"message": "Password actualizado correctamente"})
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    
    @action(detail=True, methods=['post'])
    def assign_group(self, request, pk=None):
        usuario = self.get_object()
        group_id = request.data.get('group_id')
        
        try:
            group_name = UsuarioService.asignar_grupo(
                usuario=usuario,
                group_id=group_id,
                usuario_solicitante=request.user
            )
            
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Asignó usuario {usuario.email} al grupo {group_name}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )
            
            return Response({"message": f"Usuario asignado al grupo {group_name}"})
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Group.DoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['delete'])
    def remove_group(self, request, pk=None):
        usuario = self.get_object()
        group_id = request.data.get('group_id')
        
        try:
            group_name = UsuarioService.remover_grupo(
                usuario=usuario,
                group_id=group_id,
                usuario_solicitante=request.user
            )
            
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Removió usuario {usuario.email} del grupo {group_name}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )
            
            return Response({"message": f"Usuario removido del grupo {group_name}"})
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Group.DoesNotExist:
            return Response(
                {"error": "Grupo no encontrado"},
                status=status.HTTP_404_NOT_FOUND
            )


class GroupViewSet(PermisosMixin, BitacoraModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    bitacora_modulo = "Grupo"
    modulo_permisos = "grupo"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Group.objects.all()
        return Group.objects.none()

    @action(detail=True, methods=['post'])
    def set_permissions(self, request, pk=None):
        group = self.get_object()
        permission_ids = request.data.get('permission_ids', [])

        try:
            count = UsuarioService.asignar_permisos_grupo(
                group=group,
                permission_ids=permission_ids,
                usuario_solicitante=request.user
            )
            
            RegistroBitacora.registrar(
                usuario=request.user,
                accion=f"Asignó {count} permisos al grupo {group.name}",
                ip=self.get_client_ip(),
                modulo=self.bitacora_modulo
            )

            return Response({'message': 'Permisos asignados correctamente'})
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {"error": "Error al asignar permisos"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        permisos = []
        if request.user.rol:
            permisos = list(request.user.rol.permisos.values_list('codename', flat=True))
        return Response({'permisos': permisos})


class MisPermisosEstructuradosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(request.user.permisos_dict)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            response_data = AuthService.login(
                email=email,
                password=password,
                ip=self._get_client_ip(request)
            )
            return Response(response_data)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except PermissionError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            response_data = AuthService.register(
                data=request.data,
                ip=self._get_client_ip(request)
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        
        try:
            AuthService.logout(
                refresh_token=refresh_token,
                usuario=request.user,
                ip=self._get_client_ip(request)
            )
            return Response({"message": "Sesión cerrada correctamente"})
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip