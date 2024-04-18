"""
Test cases for PaymentMethod Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import (
    PaymentMethod,
    PaymentMethodType,
    CreditCard,
    PayPal,
    DataValidationError,
    db,
)
from service.models.payment_method import convert_str_to_payment_method_type_enum

from tests.factories import (
    CreditCardFactory,
    PayPalFactory,
    generate_random_payment_methods,
)

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  PaymentMethod   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

    # pylint: disable=duplicate-code
    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(PaymentMethod).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""


class TestPaymentMethodModel(TestCaseBase):
    """PaymentMethod Model CRUD tests"""

    def test_query_all_payment_methods(self):
        """It should add and query different payment methods from the database via PaymentMethod API"""
        payment_methods = generate_random_payment_methods()
        for payment_method in payment_methods:
            payment_method.create()

        self.assertEqual(len(PaymentMethod.all()), len(payment_methods))

    def test_delete_specific_payment_methods(self):
        """Should delete PaymentMethod regardless of which type"""
        credit_card = CreditCardFactory()
        paypal = PayPalFactory()
        credit_card.create()
        paypal.create()
        self.assertEqual(len(PaymentMethod.all()), 2)
        PaymentMethod.delete(credit_card)
        PaymentMethod.delete(paypal)
        self.assertEqual(len(PaymentMethod.all()), 0)

    def test_delete_non_existing_payment_method(self):
        """It should raise an exception when deleting non existing method"""
        credit_card = CreditCardFactory()
        with self.assertRaises(DataValidationError):
            PaymentMethod.delete(credit_card)

    def test_find_payment_method_by_name(self):
        """It should find PaymentMethod by name"""
        paypal = PayPalFactory()
        paypal.create()
        found_paypal = PaymentMethod.find_by_name(paypal.name)
        self.assertEqual(paypal, found_paypal[0])

    def test_find_payment_method_by_type(self):
        """It should find PaymentMethod by type"""
        paypal = PayPalFactory()
        paypal.create()
        found_paypal = PaymentMethod.find_by_type(PaymentMethodType.PAYPAL)
        self.assertEqual(paypal, found_paypal[0])
        found_creditcard = PaymentMethod.find_by_type(PaymentMethodType.CREDIT_CARD)
        self.assertEqual(len(found_creditcard.all()), 0)

    def test_find_payment_method_by_user_id(self):
        """It should find PaymentMethod by type"""
        paypal = PayPalFactory()
        uid = paypal.user_id
        paypal.create()
        found_uid = PaymentMethod.find_by_user_id(uid)
        self.assertEqual(paypal, found_uid[0])
        found_alt_uid = PaymentMethod.find_by_user_id(uid + 1)
        self.assertEqual(len(found_alt_uid.all()), 0)

    def test_create_invalid_payment_method(self):
        """It should not create a PaymentMethod with invalid data"""
        payment_method = PaymentMethod(name="")
        with self.assertRaises(DataValidationError):
            payment_method.create()

    def test_set_payment_method_as_default(self):
        """It should set a payment method as the default"""
        user_id = 1
        payment_method = CreditCardFactory(user_id=user_id)
        payment_method.create()
        self.assertFalse(payment_method.is_default)

        payment_method.set_default_for_user()

        updated_payment_method = PaymentMethod.query.get(payment_method.id)
        self.assertTrue(updated_payment_method.is_default)

    def test_unset_other_payment_methods_when_one_is_set_as_default(self):
        """It should unset other payment methods when one is set as default"""
        user_id = 1
        payment_method1 = CreditCardFactory(user_id=user_id, is_default=False)
        payment_method2 = PayPalFactory(user_id=user_id, is_default=False)
        payment_method1.create()
        payment_method2.create()

        payment_method1.set_default_for_user()

        updated_method1 = PaymentMethod.find(payment_method1.id)
        updated_method2 = PaymentMethod.find(payment_method2.id)

        self.assertTrue(updated_method1.is_default)
        self.assertFalse(updated_method2.is_default)

    def test_default_status_persists_across_updates(self):
        """It should maintain the default status across updates"""
        payment_method = CreditCardFactory(is_default=True)
        payment_method.create()

        payment_method.set_default_for_user()

        payment_method.name = "Updated Name"
        payment_method.update()

        updated_payment_method = PaymentMethod.find(payment_method.id)
        self.assertTrue(updated_payment_method.is_default)


class TestPayPalModel(TestCaseBase):
    """PayPal Model CRUD Tests"""

    def test_deserialize_paypal(self):
        """It should deserialize a correct PayPal object"""
        fake_paypal = PayPalFactory()
        data = fake_paypal.serialize()
        paypal = PayPal()
        paypal.deserialize(data)
        self.assertTrue(paypal is not None)
        self.assertEqual(paypal.id, None)
        self.assertEqual(paypal.name, fake_paypal.name)
        self.assertEqual(paypal.type, PaymentMethodType.PAYPAL)
        self.assertEqual(paypal.email, fake_paypal.email)

    def test_deserialize_paypal_missing_data(self):
        """It should not deserialize a PayPal with missing data"""
        data = {"name": "abc"}
        paypal = PayPal()
        self.assertRaises(DataValidationError, paypal.deserialize, data)

    def test_deserialize_paypal_wrong_data(self):
        """It should not deserialize a PayPal with missing data"""
        data = PayPalFactory().serialize()
        del data["email"]
        data["email"] = 1
        paypal = PayPal()
        self.assertRaises(DataValidationError, paypal.deserialize, data)

    def test_create_paypal_with_wrong_email(self):
        """It should raise a FieldErrorException when creating PayPal with wrong email"""
        paypal = PayPal()
        rest_args = paypal.serialize()
        del rest_args["email"]

        with self.assertRaises(DataValidationError):
            PayPal(
                **rest_args,
                email="aa.com",
            )


class TestCreditCardModel(TestCaseBase):
    """CreditCard Model CRUD Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_credit_card(self):
        """It should Create a credit card and assert that it exists"""
        fake_credit_card = CreditCardFactory()
        credit_card = CreditCard(**fake_credit_card.serialize())
        self.assertEqual(
            str(credit_card),
            f"<PaymentMethod {fake_credit_card.name} id=[None]>",
        )
        self.assertTrue(credit_card is not None)
        self.assertEqual(credit_card.id, None)
        self.assertEqual(credit_card.name, fake_credit_card.name)
        self.assertEqual(credit_card.type, fake_credit_card.type.value)
        self.assertEqual(credit_card.first_name, fake_credit_card.first_name)
        self.assertEqual(credit_card.last_name, fake_credit_card.last_name)
        self.assertEqual(credit_card.card_number, fake_credit_card.card_number)
        self.assertEqual(credit_card.expiry_month, fake_credit_card.expiry_month)
        self.assertEqual(credit_card.expiry_year, fake_credit_card.expiry_year)
        self.assertEqual(credit_card.security_code, fake_credit_card.security_code)
        self.assertEqual(credit_card.billing_address, fake_credit_card.billing_address)
        self.assertEqual(credit_card.zip_code, fake_credit_card.zip_code)

    def test_deserialize_credit_card(self):
        """It should deserialize a correct CreditCard object"""
        fake_credit_card = CreditCardFactory()
        data = fake_credit_card.serialize()
        credit_card = CreditCard()
        credit_card.deserialize(data)
        self.assertEqual(
            str(credit_card),
            f"<PaymentMethod {fake_credit_card.name} id=[None]>",
        )
        self.assertTrue(credit_card is not None)
        self.assertEqual(credit_card.id, None)
        self.assertEqual(credit_card.name, fake_credit_card.name)
        self.assertEqual(credit_card.type, PaymentMethodType.CREDIT_CARD)
        self.assertEqual(credit_card.first_name, fake_credit_card.first_name)
        self.assertEqual(credit_card.last_name, fake_credit_card.last_name)
        self.assertEqual(credit_card.card_number, fake_credit_card.card_number)
        self.assertEqual(credit_card.expiry_month, fake_credit_card.expiry_month)
        self.assertEqual(credit_card.expiry_year, fake_credit_card.expiry_year)
        self.assertEqual(credit_card.security_code, fake_credit_card.security_code)
        self.assertEqual(credit_card.billing_address, fake_credit_card.billing_address)
        self.assertEqual(credit_card.zip_code, fake_credit_card.zip_code)

    def test_deserialize_credit_card_missing_data(self):
        """It should not deserialize a CreditCard with missing data"""
        data = {"name": "Payments for gas"}
        credit_card = CreditCard()
        self.assertRaises(DataValidationError, credit_card.deserialize, data)

    def test_deserialize_credit_card_bad_data(self):
        """It should not deserialize a CreditCard with bad data"""
        data = "this is str"
        credit_card = CreditCard()
        self.assertRaises(DataValidationError, credit_card.deserialize, data)

    def test_deserialize_credit_card_bad_attributes(self):
        """It should not deserialize a CreditCard with bad attributes"""
        data = {
            "id": None,
            "name": 123,
            "type": "cash",
            "first_name": 1,
            "last_name": 2,
            "card_number": 3,
            "expiry_month": "-3",
            "expiry_year": "-1",
            "security_code": 11111,
            "billing_address": 0,
            "zip_code": 0,
        }
        credit_card = CreditCard()
        self.assertRaises(DataValidationError, credit_card.deserialize, data)

    def test_create_credit_card_with_invalid_card_number(self):
        """It should raise FieldValidationError when card_number is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["card_number"]

        with self.assertRaises(DataValidationError):
            CreditCard(
                **rest_args,
                card_number="1",
            )
        with self.assertRaises(DataValidationError):
            CreditCard(
                **rest_args,
                card_number="abc",
            )
        with self.assertRaises(DataValidationError):
            CreditCard(
                **rest_args,
                card_number=123,
            )

    def test_create_credit_card_with_invalid_first_name(self):
        """It should raise FieldValidationError when first_name is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["first_name"]

        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, first_name=123)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, first_name="123")

    def test_create_credit_card_with_invalid_last_name(self):
        """It should raise FieldValidationError when last_name is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["last_name"]

        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, last_name=123)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, last_name="123")

    def test_create_credit_card_with_invalid_expiry_month(self):
        """It should raise FieldValidationError when expiry_month is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["expiry_month"]

        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, expiry_month=13)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, expiry_month=-1)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, expiry_month="abc")

    def test_create_credit_card_with_invalid_expiry_year(self):
        """It should raise FieldValidationError when expiry_year is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["expiry_year"]

        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, expiry_year=-10)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, expiry_year=40010)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, expiry_year="abc")

    def test_create_credit_card_with_invalid_security_code(self):
        """It should raise FieldValidationError when security_code is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["security_code"]

        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, security_code=1234)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, security_code="code123!")
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, security_code="1000")

    def test_create_credit_card_with_invalid_zip_code(self):
        """It should raise FieldValidationError when zip_code is invalid"""
        credit_card = CreditCardFactory()
        rest_args = credit_card.serialize()
        del rest_args["zip_code"]

        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, zip_code=123456)
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, zip_code="abcdefg")
        with self.assertRaises(DataValidationError):
            CreditCard(**rest_args, zip_code="1000")

    def test_add_a_credit_card_to_db(self):
        """It should Create a CreditCard and add it to the database"""
        credit_cards = CreditCard.all()
        self.assertEqual(credit_cards, [])
        credit_card = CreditCardFactory()
        self.assertTrue(credit_card is not None)
        self.assertEqual(credit_card.id, None)
        credit_card.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(credit_card.id)
        credit_cards = CreditCard.all()
        self.assertEqual(len(credit_cards), 1)

    def test_read_a_credit_card_from_db(self):
        """It should Read a CreditCard from the database"""
        credit_card = CreditCardFactory()
        logging.debug(credit_card)
        credit_card.id = None
        credit_card.create()
        self.assertIsNotNone(credit_card.id)
        # Fetch it back
        found_credit_card = CreditCard.find(credit_card.id)
        self.assertEqual(found_credit_card.id, credit_card.id)
        self.assertEqual(found_credit_card.name, credit_card.name)
        self.assertEqual(found_credit_card.type, PaymentMethodType.CREDIT_CARD)
        self.assertEqual(found_credit_card.first_name, credit_card.first_name)
        self.assertEqual(found_credit_card.last_name, credit_card.last_name)
        self.assertEqual(found_credit_card.card_number, credit_card.card_number)
        self.assertEqual(found_credit_card.expiry_month, credit_card.expiry_month)
        self.assertEqual(found_credit_card.expiry_year, credit_card.expiry_year)
        self.assertEqual(found_credit_card.security_code, credit_card.security_code)
        self.assertEqual(found_credit_card.billing_address, credit_card.billing_address)
        self.assertEqual(found_credit_card.zip_code, credit_card.zip_code)

    def test_update_a_credit_card_in_db(self):
        """It should Update a CreditCard"""
        credit_card = CreditCardFactory()
        logging.debug(credit_card)
        credit_card.id = None
        credit_card.create()
        # logging.debug(payment)
        self.assertIsNotNone(credit_card.id)
        # Change it and save it
        new_name = "Test name"
        credit_card.name = new_name
        original_id = credit_card.id
        credit_card.update()
        self.assertEqual(credit_card.id, original_id)
        self.assertEqual(credit_card.name, new_name)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        credit_cards = PaymentMethod.all()
        self.assertEqual(len(credit_cards), 1)
        self.assertEqual(credit_cards[0].id, original_id)
        self.assertEqual(credit_cards[0].name, new_name)

    def test_update_a_credit_card_in_db_with_no_id(self):
        """It should not Update a CreditCard with no id"""
        credit_card = CreditCardFactory()
        logging.debug(credit_card)
        credit_card.id = None
        self.assertRaises(DataValidationError, credit_card.update)

    def test_delete_a_credit_card_in_db(self):
        """It should Delete a CreditCard"""
        payment = CreditCardFactory()
        payment.create()
        self.assertEqual(len(CreditCard.all()), 1)
        # delete the payment and make sure it isn't in the database
        payment.delete()
        self.assertEqual(len(CreditCard.all()), 0)

    def test_convert_str_to_payment_method_type_enum(self):
        """It should Match the enum value to enum"""
        self.assertEqual(
            convert_str_to_payment_method_type_enum(PaymentMethodType.UNKNOWN.value),
            PaymentMethodType.UNKNOWN,
        )
        self.assertEqual(
            convert_str_to_payment_method_type_enum(PaymentMethodType.UNKNOWN),
            PaymentMethodType.UNKNOWN,
        )
        self.assertEqual(convert_str_to_payment_method_type_enum(123), None)
