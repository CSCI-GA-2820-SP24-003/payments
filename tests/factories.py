"""
Factories for tests
"""

import random
from factory.fuzzy import FuzzyInteger
from factory import Factory, Faker
from service.models import PaymentMethod, CreditCard, PayPal


class PaymentMethodFactory(Factory):
    """Creates fake PaymentMethod"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Persistent class"""

        model = PaymentMethod

    name = Faker("name")
    user_id = FuzzyInteger(0, 1000)
    is_default = False


class CreditCardFactory(PaymentMethodFactory):
    """Creates fake CreditCard"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Persistent class"""

        model = CreditCard

    first_name = Faker("first_name")
    last_name = Faker("last_name")
    card_number = Faker("credit_card_number", card_type="visa16")
    expiry_month = FuzzyInteger(1, 12)
    expiry_year = FuzzyInteger(2024, 2050)
    security_code = Faker("credit_card_security_code", card_type="visa16")
    billing_address = Faker("address")
    zip_code = Faker("zipcode")


class PayPalFactory(PaymentMethodFactory):
    """Creates fake PayPal"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Persistent class"""

        model = PayPal

    email = Faker("email")


def generate_random_payment_methods(count=10):
    """Generates a list of random PaymentMethod instances"""
    payment_methods = []
    for _ in range(count):
        random_choice = random.choice([CreditCardFactory, PayPalFactory])
        method = random_choice()
        payment_methods.append(method)

    return payment_methods
