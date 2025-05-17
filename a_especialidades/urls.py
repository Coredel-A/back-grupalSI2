from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstablecimientoViewSet

router = DefaultRouter()
router.register(r'', EstablecimientoViewSet)

urlpatterns = [
    path('',include(router.urls)),
]