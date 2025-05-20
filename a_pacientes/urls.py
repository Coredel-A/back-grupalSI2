from django.urls import path, include
from rest_framework.routers import DefaultRouter
from.views import PacientesViewSet

router = DefaultRouter()
router.register(r'', PacientesViewSet, basename='pacientes')

urlpatterns = [
    path('', include(router.urls)),
]