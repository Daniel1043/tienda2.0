import django_filters
from .models import Marca, Producto

class ProductoXmarcaFilter(django_filters.FilterSet):
    # Utiliza ModelChoiceFilter para obtener automáticamente las opciones de todas las marcas
    marca = django_filters.ChoiceFilter(choices=Marca.objects.values_list("id","nombre"), empty_label='TODO')
    nombre = django_filters.CharFilter(lookup_expr='icontains')  # Utiliza icontains para búsquedas case-insensitive

    class Meta:
        model = Producto
        fields = ['marca','nombre']

