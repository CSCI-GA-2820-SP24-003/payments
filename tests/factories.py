# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate, FuzzyInteger
from service.models import PaymentMethod, PaymentType


class PaymentFactory(factory.Factory):
    """Factory for creating fake PaymentMethod instances for testing."""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = PaymentMethod

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("first_name")
    payment_type = FuzzyChoice(choices=[PaymentType.CREDIT_CARD, PaymentType.PAYPAL, PaymentType.UNKNOWN])
    payment_type_id = FuzzyInteger(1000, 9999)  # Assuming an arbitrary range for example
    user_id = FuzzyInteger(1, 1000)  # Simulating user IDs in an arbitrary range
