from decimal import Decimal
from math import ceil


def calculate_rental_cost(instance):
    """Функция для расчёта стоимости аренды велосипеда."""

    if instance.status == "pending":
        duration_sec = (
                instance.end_time - instance.start_time
        ).total_seconds()  # время аренды в секундах
        duration_hours = ceil(duration_sec / 3600)  # время аренды в часах

        # расчёт стоимости при аренде больше суток
        if duration_hours > 24:
            days = duration_hours // 24  # кол-во суток
            cost_days = (
                    days * instance.rented_bike.rental_cost_day
            )  # стоимость за все дни аренды
            cost_hours = (
                                 duration_hours % 24
                         ) * instance.rented_bike.rental_cost_hour  # стоимость за все часы аренды
            total_cost = Decimal(cost_days) + Decimal(cost_hours)  # общая стоимость за дни и часы

        # расчёт стоимости почасовой аренды
        else:
            total_cost = Decimal(duration_hours * instance.rented_bike.rental_cost_hour)
        return Decimal(total_cost)
    else:
        return None
