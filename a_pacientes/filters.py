import django_filters
from django.db.models import Q
from .models import Pacientes

class PacientesFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    apellido = django_filters.CharFilter(lookup_expr='icontains')
    ci = django_filters.CharFilter(lookup_expr='icontains')
    sexo = django_filters.ChoiceFilter(choices=Pacientes.SEXO_CHOICES)
    asegurado = django_filters.BooleanFilter()
    beneficiario_de = django_filters.UUIDFilter(field_name='beneficiario_de__id')
    fecha_nacimiento = django_filters.DateFromToRangeFilter()
    
    # Búsqueda general en múltiples campos
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Pacientes
        fields = [
            'nombre',
            'apellido', 
            'ci',
            'sexo',
            'asegurado',
            'beneficiario_de',
            'fecha_nacimiento',
            'search',
        ]
    
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(nombre__icontains=value) |
            Q(apellido__icontains=value) |
            Q(ci__icontains=value)
        )