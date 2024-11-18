from django_filters import rest_framework as filters

from .models import Payment


class PaymentFilterSet(filters.FilterSet):
    method = filters.ChoiceFilter(field_name='method', choices=Payment.PAYMENT_METHOD_CHOICES,
                                  empty_label='Not selected')
    bike_brand = filters.CharFilter(field_name='rental__rented_bike__brand', lookup_expr='icontains')

    class Meta:
        model = Payment
        fields = ['method', 'bike_brand']
