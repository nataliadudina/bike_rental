from rest_framework.pagination import PageNumberPagination


class RentHistoryPaginator(PageNumberPagination):
    """ Пагинация для истории аренды пользователя. """

    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 10


class PaymentsPaginator(PageNumberPagination):
    """ Пагинация для истории платежей пользователя. """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20
