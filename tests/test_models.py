"""
Test cases for PaymentMethod Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

from service.models import (
    PaymentMethod,
    PaymentType,
    DataValidationError,
    db,
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
    """PaymentMethod Model CRUD Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_payment(self):
        """It should Create a payment and assert that it exists"""
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.CREDIT_CARD,
            payment_type_id=1,
            user_id=1,
        )
        self.assertEqual(str(payment), "<PaymentMethod payment1 id=[None]>")
        self.assertTrue(payment is not None)
        self.assertEqual(payment.id, None)
        self.assertEqual(payment.name, "payment1")
        self.assertEqual(payment.payment_type, PaymentType.CREDIT_CARD)
        self.assertEqual(payment.payment_type_id, 1)
        self.assertEqual(payment.user_id, 1)
        payment = PaymentMethod(
            name="payment2",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        self.assertEqual(payment.payment_type, PaymentType.PAYPAL)

    def test_add_a_payment(self):
        """It should Create a payment and add it to the database"""
        payments = PaymentMethod.all()
        self.assertEqual(payments, [])
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        self.assertTrue(payment is not None)
        self.assertEqual(payment.id, None)
        payment.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(payment.id)
        payments = PaymentMethod.all()
        self.assertEqual(len(payments), 1)

    def test_read_a_payment(self):
        """It should Read a PaymentMethod"""
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        logging.debug(payment)
        payment.id = None
        payment.create()
        self.assertIsNotNone(payment.id)
        # Fetch it back
        found_payment = PaymentMethod.find(payment.id)
        self.assertEqual(found_payment.id, payment.id)
        self.assertEqual(found_payment.name, payment.name)
        self.assertEqual(found_payment.payment_type_id, payment.payment_type_id)

    def test_update_a_payment(self):
        """It should Update a PaymentMethod"""
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        logging.debug(payment)
        payment.id = None
        payment.create()
        # logging.debug(payment)
        self.assertIsNotNone(payment.id)
        # Change it and save it
        payment.payment_type = PaymentType.CREDIT_CARD
        original_id = payment.id
        payment.update()
        self.assertEqual(payment.id, original_id)
        self.assertEqual(payment.payment_type, PaymentType.CREDIT_CARD)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        payments = PaymentMethod.all()
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0].id, original_id)
        self.assertEqual(payments[0].payment_type, PaymentType.CREDIT_CARD)

    def test_update_no_id(self):
        """It should not Update a PaymentMethod with no id"""
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        logging.debug(payment)
        payment.id = None
        self.assertRaises(DataValidationError, payment.update)

    def test_delete_a_payment(self):
        """It should Delete a PaymentMethod"""
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.CREDIT_CARD,
            payment_type_id=1,
            user_id=1,
        )
        payment.create()
        self.assertEqual(len(PaymentMethod.all()), 1)
        # delete the payment and make sure it isn't in the database
        payment.delete()
        self.assertEqual(len(PaymentMethod.all()), 0)

    def test_list_all_payments(self):
        """It should List all PaymentMethods in the database"""
        payments = PaymentMethod.all()
        self.assertEqual(payments, [])
        # Create 5 PaymentMethods
        payment_types = [PaymentType.CREDIT_CARD, PaymentType.PAYPAL]
        for i in range(5):
            payment = PaymentMethod(
                name="payment_" + str(i),
                payment_type=payment_types[i % 2],
                payment_type_id=1,
                user_id=1,
            )
            payment.create()
        # See if we get back 5 payments
        payments = PaymentMethod.all()
        self.assertEqual(len(payments), 5)

    def test_serialize_a_payment(self):
        """It should serialize a PaymentMethod"""
        payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        data = payment.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], payment.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], payment.name)
        self.assertIn("user_id", data)
        self.assertEqual(data["user_id"], payment.user_id)
        self.assertIn("payment_type", data)
        self.assertEqual(data["payment_type"], payment.payment_type.name)
        self.assertIn("payment_type_id", data)
        self.assertEqual(data["payment_type_id"], payment.payment_type_id)

    def test_deserialize_a_payment(self):
        """It should de-serialize a PaymentMethod"""
        data = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        ).serialize()
        payment = PaymentMethod()
        payment.deserialize(data)
        self.assertNotEqual(payment, None)
        self.assertEqual(payment.id, None)
        self.assertEqual(payment.name, data["name"])
        self.assertEqual(payment.payment_type.name, data["payment_type"])
        self.assertEqual(payment.payment_type_id, data["payment_type_id"])
        self.assertEqual(payment.user_id, data["user_id"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a PaymentMethod with missing data"""
        data = {"id": 1, "name": "Kitty", "category": "cat"}
        payment = PaymentMethod()
        self.assertRaises(DataValidationError, payment.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        payment = PaymentMethod()
        self.assertRaises(DataValidationError, payment.deserialize, data)

    def test_deserialize_bad_gender(self):
        """It should not deserialize a bad gender attribute"""
        test_payment = PaymentMethod(
            name="payment1",
            payment_type=PaymentType.PAYPAL,
            payment_type_id=1,
            user_id=1,
        )
        data = test_payment.serialize()
        data["payment_type"] = "paypal"  # wrong case
        payment = PaymentMethod()
        self.assertRaises(DataValidationError, payment.deserialize, data)
