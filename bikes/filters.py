from django_filters import rest_framework as filters

from bikes.models import Bicycle


class BikeFilterSet(filters.FilterSet):
    """ Фильтры для фильтрации велосипедов по бренду, состоянию и типу."""

    brand = filters.CharFilter(field_name='brand')
    condition = filters.ChoiceFilter(choices=Bicycle.CONDITION_CHOICES, empty_label='Not selected')
    type = filters.ChoiceFilter(choices=Bicycle.TYPE_CHOICES, empty_label='Not selected')

    class Meta:
        model = Bicycle
        fields = {
            'brand': ['exact', 'icontains'],
            'condition': ['exact'],
            'type': ['exact'],
        }
