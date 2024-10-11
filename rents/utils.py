from math import ceil

from django.utils.timezone import now


def calculate_rental_cost(instance):
    """Функция для расчёта стоимости аренды велосипеда."""

    if instance.status == "completed":
        instance.end_time = now()
        start_time = instance.start_time
        duration_sec = (
            instance.end_time - start_time
        ).total_seconds()  # время аренды в секундах
        duration_hours = ceil(duration_sec / 3600)  # время аренды в часах
        print(duration_hours, "hours")  # УДАЛИТЬ!!!

        # расчёт стоимости при аренде больше суток
        if duration_hours > 24:
            days = duration_hours // 24  # кол-во суток
            cost_days = (
                days * instance.rented_bike.rental_cost_day
            )  # стоимость за все дни аренды
            cost_hours = (
                duration_hours % 24
            ) * instance.rented_bike.rental_cost_hour  # стоимость за все часы аренды
            total_cost = cost_days + cost_hours  # общая стоимость за дни и часы

        # расчёт стоимости почасовой аренды
        else:
            total_cost = duration_hours * instance.rented_bike.rental_cost_hour

        print(total_cost, "$")  # УДАЛИТЬ!!!
        return total_cost
    else:
        return None
