from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UsuarioViewSet, LoginView, RegisterView, LogoutView, GroupViewSet, PermissionListView, MisPermisosView, MisPermisosEstructuradosView

router = DefaultRouter()
router.register(r'grupos', GroupViewSet)
router.register(r'', UsuarioViewSet)

urlpatterns = [
    path('permisos/', PermissionListView.as_view(), name='listar-permisos'),
    path('mis-permisos-estructurados/', MisPermisosEstructuradosView.as_view(), name='mis-permisos-estructurados'),
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='toke_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]