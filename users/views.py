from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from stripe import StripeError

from rents.models import Rental
from rents.paginators import PaymentsPaginator
from users.models import Payment
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator
from users.serializers import UserSerializer, BikeRentalHistorySerializer, PaymentSerializer
from users.services import create_stripe_product, create_stripe_price, create_stripe_checkout_session, \
    retrieve_stripe_checkout_session


class UserApiList(generics.ListAPIView):
    """Представление для вывода списка пользователей."""

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated, IsModerator]


class UserRegistrationAPIView(generics.CreateAPIView):
    """Представление для создания / регистрации пользователя."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        password = self.request.data.get("password")
        if password:
            user.set_password(password)
            user.save()


class UserApiDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Представление для чтения, обновления удаления записи о пользователе в бд."""

    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    def perform_update(self, serializer):
        user = serializer.save()
        password = self.request.data.get("password")
        if password:
            user.set_password(password)
            user.save()

    def get_permissions(self):
        """Проверка прав доступа для изменения профиля."""

        # Определяем права доступа на основе метода запроса
        if self.request.method == "GET":
            permission_classes = (IsAuthenticated, IsOwnerOrModerator)
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = (IsAuthenticated, IsOwner)
        self.permission_classes = permission_classes
        return super().get_permissions()


class UserRentHistory(APIView):
    """ Представление для просмотра истории аренды велосипедов пользователя."""

    permission_classes = [IsAuthenticated]
    serializer_class = BikeRentalHistorySerializer

    def get(self, request):
        history = Rental.objects.filter(renter=self.request.user)
        serializer = self.serializer_class(history, many=True)
        return Response(serializer.data)


class CreatePaymentView(APIView):
    """Представление для создания ссылки на оплату."""

    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def post(self, request):
        rental_id = request.data.get('rental_id')
        if not rental_id:
            return Response({'error': 'Rental ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_email = request.user.email

        try:
            # Получает запись об аренде
            rental = get_object_or_404(Rental, id=rental_id)
            user = rental.renter
            if request.user != user:
                return Response({"error": "Not authorized to return this bike."},
                                status=status.HTTP_403_FORBIDDEN, )

            if rental.status != 'pending':
                return Response({'error': 'Invalid rental status'}, status=status.HTTP_400_BAD_REQUEST)

            if rental.rental_cost <= 0:
                return Response({'error': 'Invalid rental cost'}, status=status.HTTP_400_BAD_REQUEST)

            # Создает продукт и цену в Stripe
            product = create_stripe_product(rental)
            price = create_stripe_price(product, rental.rental_cost)

            # Создает сессию оплаты
            session = create_stripe_checkout_session(price.id, user_email)

            # Создает платеж в системе
            payment = Payment.objects.create(
                user=request.user,
                rental=rental,
                amount=rental.rental_cost,
                method='transfer',
                session_id=session.id,
                payment_link=session.url,
                stripe_product_id=product.id
            )

            # Возвращает ссылку на оплату
            return Response({'payment_url': session.url}, status=status.HTTP_201_CREATED)
        except StripeError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    """
        Представление для обработки статуса платежа после успешной оплаты через Stripe.
        Ожидает параметр 'session_id' в GET-запросе, использует его для получения информации о сессии оплаты из Stripe
        и обновления статуса платежа в базе данных.
        Переход на страницу статуса платежа переходит автоматически после успешной оплаты.
    """

    serializer_class = PaymentSerializer

    def get(self, request, *args, **kwargs):
        # Получаем ID сессии из параметров запроса
        session_id = request.GET.get('session_id')

        if not session_id:
            # Возвращаем ошибку, если session_id не предоставлен
            return Response({'error': 'Session ID is required'}, status=400)

        try:
            # Получаем информацию о сессии оплаты из Stripe
            session = retrieve_stripe_checkout_session(session_id)
            payment_status = session.payment_status

            # Находим платеж в базе данных по stripe_session_id
            payment = get_object_or_404(Payment, session_id=session_id)

            if payment:
                # Сохраняем статус платежа в базе данных
                payment.status = payment_status
                print(f"Payment status from Stripe: {payment_status}")

                # Обновляем статус аренды
                if payment_status == 'paid':
                    rental = payment.rental
                    rental.status = 'completed'
                    rental.save()  # Обновляем статус аренды

                payment.save()

            # Возвращаем подтверждение об оплате
            return Response({'message': 'Payment is accepted'}, status=status.HTTP_202_ACCEPTED)
        except StripeError as e:
            # Возвращаем ошибку, если произошла ошибка при взаимодействии с Stripe API
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    # filter_backends = [DjangoFilterBackend, OrderingFilter]  # Бэкенд для обработки фильтра
    ordering_fields = ('date',)
    queryset = Payment.objects.all()
    pagination_class = PaymentsPaginator
    permission_classes = [IsAuthenticated | IsModerator]

    def get_queryset(self):
        # Показывает только платежи пользователя
        if not self.request.user.groups.filter(name='moderators').exists():
            return Payment.objects.filter(user=self.request.user)
        # Для модератора показывает все
        return Payment.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.get_serializer(paginated_queryset, many=True)
        if not paginated_queryset:
            return Response({'message': 'No payments to display.'}, status=200)
        return paginator.get_paginated_response(serializer.data)
