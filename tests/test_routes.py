"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from tests.factories import CreditCardFactory, PayPalFactory
from service.common import status
from service.models import db, PaymentMethod

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/payment-method"
LIST_URL = BASE_URL + "s"

######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPaymentsService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(PaymentMethod).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_index(self):
        """It should call the home page and receive information about existing methods"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        methods = data["methods"]
        self.assertEqual(data["status"], status.HTTP_200_OK)
        self.assertEqual(data["name"], "Payments service")
        self.assertEqual(data["version"], "1.0")
        self.assertEqual(len(methods), 5)

        # check if root path has definitions for all methods
        def is_path_and_method_in_list(path, method):
            return any(
                item["path"] == path and item["method"] == method for item in methods
            )

        self.assertTrue(
            is_path_and_method_in_list(path="/payment-methods", method="GET")
        )
        self.assertTrue(
            is_path_and_method_in_list(path="/payment-method/:id", method="GET")
        )
        self.assertTrue(
            is_path_and_method_in_list(path="/payment-method", method="POST")
        )
        self.assertTrue(
            is_path_and_method_in_list(path="/payment-method/:id", method="DELETE")
        )
        self.assertTrue(
            is_path_and_method_in_list(path="/payment-method/:id", method="PUT")
        )

    def test_create_credit_card_payment_method(self):
        """It should create a new CreditCard"""
        credit_card = CreditCardFactory()
        resp = self.client.post(
            BASE_URL,
            json=credit_card.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check whether response matches the credit card method
        created_card = resp.get_json()
        self.assertIsNotNone(created_card["id"])
        self.assertEqual(created_card["name"], credit_card.name)
        self.assertEqual(created_card["type"], credit_card.type.value)
        self.assertEqual(created_card["user_id"], credit_card.user_id)
        self.assertEqual(created_card["first_name"], credit_card.first_name)
        self.assertEqual(created_card["last_name"], credit_card.last_name)
        self.assertEqual(created_card["card_number"], credit_card.card_number)
        self.assertEqual(created_card["expiry_year"], credit_card.expiry_year)
        self.assertEqual(created_card["expiry_month"], credit_card.expiry_month)
        self.assertEqual(created_card["security_code"], credit_card.security_code)
        self.assertEqual(created_card["zip_code"], credit_card.zip_code)
        self.assertEqual(created_card["billing_address"], credit_card.billing_address)

    def test_create_paypal_payment_method(self):
        """It should create a new PayPal"""
        paypal = PayPalFactory()
        resp = self.client.post(
            BASE_URL,
            json=paypal.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check whether response matches the paypal method
        created_paypal = resp.get_json()
        self.assertIsNotNone(created_paypal["id"])
        self.assertEqual(created_paypal["name"], paypal.name)
        self.assertEqual(created_paypal["type"], paypal.type.value)
        self.assertEqual(created_paypal["user_id"], paypal.user_id)
        self.assertEqual(created_paypal["email"], paypal.email)

    def test_create_payment_method_with_no_type(self):
        """It should respond with 400 BAD REQUEST if type is wrong"""
        data = {
            "name": "test_method",
            "user_id": 3,
            "type": "test",
            "email": "sample@email.com",
        }
        resp = self.client.post(BASE_URL, json=data, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_method_wrong_content_type(self):
        """It should respond with 415 when creating a payment method with anything but application/json"""
        resp = self.client.post(BASE_URL, content_type="text/html")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_payment_method_no_content_type(self):
        """It should respond with 415 when creating a payment method with no content type"""
        resp = self.client.post(BASE_URL, content_type=None)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_unsupported_method(self):
        """It should respond with 405 when trying to use unsupported method"""
        resp = self.client.trace(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_payment_method(self):
        """It should Update an existing Payment Method"""
        # create a payment to update
        test_payment = CreditCardFactory()
        response = self.client.post(BASE_URL, json=test_payment.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the payment
        new_payment = response.get_json()
        logging.debug(new_payment)
        new_payment["name"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_payment['id']}", json=new_payment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_payment = response.get_json()
        self.assertEqual(updated_payment["name"], "unknown")

    def test_delete_payment_method(self):
        """It should Delete a Payment Method"""
        test_payment_method = CreditCardFactory()
        test_payment_method.create()
        response = self.client.delete(f"{BASE_URL}/{test_payment_method.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_payment_method.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_payment_methods(self):
        """It should List all PaymentMethods"""
        first_payment_method = CreditCardFactory()
        first_payment_method.create()
        second_payment_method = CreditCardFactory()
        second_payment_method.create()
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        response = self.client.get(f"{LIST_URL}?name={second_payment_method.name}")
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], second_payment_method.serialize())

    def test_get_payment_method(self):
        """It should Get a single PaymentMethod"""
        test_payment_method = CreditCardFactory()
        test_payment_method.create()
        response = self.client.get(f"{BASE_URL}/{test_payment_method.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_payment_method.name)
