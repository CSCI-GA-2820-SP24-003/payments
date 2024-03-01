"""
Factories for tests
"""

from factory.fuzzy import FuzzyInteger
from factory import Factory, Faker
from service.models import CreditCard


class CreditCardFactory(Factory):
    """Creates fake Credit Card object"""

    class Meta:
        """Persistent class"""

        model = CreditCard

    id = FuzzyInteger(0, 1000)
    payment_method_id = FuzzyInteger(0, 1000)
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    card_number = Faker("credit_card_number", card_type="visa16")
    expiry_month = FuzzyInteger(1, 12)
    expiry_year = FuzzyInteger(2024, 2050)
    security_code = Faker("credit_card_security_code")
    billing_address = Faker("address")
    zip_code = Faker("zipcode")
