import django_filters
from django.db.models import Q, Exists, OuterRef
from .models import Establecimiento,Especialidad

class EstablecimientoFilter(django_filters.FilterSet):
    nombre = django_filters.CharFilter(lookup_expr='icontains')
    tipo_establecimiento = django_filters.CharFilter()
    nivel = django_filters.CharFilter()
    especialidades = django_filters.ModelMultipleChoiceFilter(
        field_name='especialidades__id',
        to_field_name='id',
        queryset=Especialidad.objects.all()
    )

    tiene_especialidades = django_filters.BooleanFilter(
        method='filter_tiene_especialidades'
    )

    especialidades_ids = django_filters.CharFilter(
        method='filter_especialidades_ids'
    )

    class Meta:
        model = Establecimiento
        fields = ['nombre', 'tipo_establecimiento', 'nivel', 'especialidades', 'tiene_especialidades']

    def filter_tiene_especialidades(self, queryset, name, value):
        if value is True:
            return queryset.filter(especialidades__isnull=False).distinct()
        elif value is False:
            return queryset.filter(especialidades__isnull=True).distinct()
        return queryset
    
    def filter_especialidades_ids(self, queryset, name, value):
        if value:
            try:
                ids = [int(id.strip()) for id in value.split(',') if id.strip().isdigit()]
                if ids:
                    return queryset.filter(especialidades__id__in=ids).distinct()
            except (ValueError, AttributeError):
                pass
        
        return queryset