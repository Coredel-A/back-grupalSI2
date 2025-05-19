from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UsuarioViewSet, LoginView, RegisterView, LogoutView

router = DefaultRouter()
router.register(r'', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='toke_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
]