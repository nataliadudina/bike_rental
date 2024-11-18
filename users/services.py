import logging

import stripe

from config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


def create_stripe_product(rental):
    """Создает продукт в Stripe для курса."""
    product = stripe.Product.create(
        name=rental,
        type="service"
    )
    logging.info("Strie Product is created.")
    return product


def create_stripe_price(product_id, amount):
    """ Создаёт цену в stripe. """
    return stripe.Price.create(
        currency="usd",
        product=product_id,
        unit_amount=int(amount * 100),
    )


def create_stripe_checkout_session(price_id, user_email):
    """Создает сессию оплаты в Stripe."""
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://127.0.0.1:8000/payment-status/?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/',
            customer_email=user_email,
        )
        logging.info("Stripe Session is created.")
        return session
    except stripe.error.StripeError as e:
        logging.error(f"Failed to create session: {e}")
        return None


def retrieve_stripe_checkout_session(session_id):
    """Проверка статуса платежа"""
    session = stripe.checkout.Session.retrieve(session_id)
    return session
