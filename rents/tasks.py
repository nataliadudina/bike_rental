import logging

from celery import shared_task

from rents.models import Rental
from rents.utils import calculate_rental_cost

logger = logging.getLogger(__name__)


@shared_task
def get_rental_cost(rental_id):
    """
    Фоновая задача для расчета платы за аренду велосипеда.

    Получает объект аренды, вызывает функцию расчета
    стоимости и возвращает результат. Если возникает ошибка, возвращает сообщение
    об ошибке.
    """
    try:
        rental = Rental.objects.get(id=rental_id)
        payment = calculate_rental_cost(rental)
        return {"status": "success", "rental_cost": float(payment)}
    except Exception as e:
        logger.error(f"Error occurred while calculating cost for {rental_id}.")
        return {"error": str(e)}
