"""
Factories for tests
"""

from factory.fuzzy import FuzzyInteger
from factory import Factory, Faker
from service.models import PaymentMethod, CreditCard


class PaymentMethodFactory(Factory):
    """Creates fake PaymentMethod"""

    class Meta:
        """Persistent class"""

        model = PaymentMethod

    name = Faker("name")
    user_id = FuzzyInteger(0, 1000)


class CreditCardFactory(PaymentMethodFactory):
    """Creates fake CreditCard"""

    class Meta:
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
