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
from service.routes import generate_apikey

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/api/payments"

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
        self.headers = {}
        db.session.query(PaymentMethod).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def test_index(self):
        """It should call the root URL and receive static index page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Payments service", response.data)

    def test_health(self):
        """It should call /health and receive status OK"""
        response = self.client.get("/health")
        self.assertEqual(response.get_json(), {"status": "OK"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_credit_card_payment_method(self):
        """It should create a new CreditCard"""
        credit_card = CreditCardFactory()
        resp = self.client.post(
            BASE_URL,
            json=credit_card.serialize(),
            content_type="application/json",
            headers=self.headers,
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

        # Check that the location header is correct
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        resp = self.client.get(location)
        new_created_card = resp.get_json()
        self.assertIsNotNone(new_created_card["id"])
        self.assertEqual(new_created_card["name"], credit_card.name)
        self.assertEqual(new_created_card["type"], credit_card.type.value)
        self.assertEqual(new_created_card["user_id"], credit_card.user_id)
        self.assertEqual(new_created_card["first_name"], credit_card.first_name)
        self.assertEqual(new_created_card["last_name"], credit_card.last_name)
        self.assertEqual(new_created_card["card_number"], credit_card.card_number)
        self.assertEqual(new_created_card["expiry_year"], credit_card.expiry_year)
        self.assertEqual(new_created_card["expiry_month"], credit_card.expiry_month)
        self.assertEqual(new_created_card["security_code"], credit_card.security_code)
        self.assertEqual(new_created_card["zip_code"], credit_card.zip_code)
        self.assertEqual(
            new_created_card["billing_address"], credit_card.billing_address
        )

    def test_create_paypal_payment_method(self):
        """It should create a new PayPal"""
        paypal = PayPalFactory()
        resp = self.client.post(
            BASE_URL,
            json=paypal.serialize(),
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Check whether response matches the paypal method
        created_paypal = resp.get_json()
        self.assertIsNotNone(created_paypal["id"])
        self.assertEqual(created_paypal["name"], paypal.name)
        self.assertEqual(created_paypal["type"], paypal.type.value)
        self.assertEqual(created_paypal["user_id"], paypal.user_id)
        self.assertEqual(created_paypal["email"], paypal.email)

        # Check that the location header is correct
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        resp = self.client.get(location)
        new_created_paypal = resp.get_json()
        self.assertIsNotNone(new_created_paypal["id"])
        self.assertEqual(new_created_paypal["name"], paypal.name)
        self.assertEqual(new_created_paypal["type"], paypal.type.value)
        self.assertEqual(new_created_paypal["user_id"], paypal.user_id)
        self.assertEqual(new_created_paypal["email"], paypal.email)

    def test_create_payment_method_with_no_type(self):
        """It should respond with 400 BAD REQUEST if type is wrong"""
        data = {
            "name": "test_method",
            "user_id": 3,
            "type": "test",
            "email": "sample@email.com",
        }
        resp = self.client.post(
            BASE_URL, json=data, content_type="application/json", headers=self.headers
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_method_wrong_content_type(self):
        """It should respond with 415 when creating a payment method with anything but application/json"""
        resp = self.client.post(
            BASE_URL, content_type="text/html", headers=self.headers
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_payment_method_no_content_type(self):
        """It should respond with 415 when creating a payment method with no content type"""
        resp = self.client.post(BASE_URL, headers=self.headers, content_type=None)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_unsupported_method(self):
        """It should respond with 405 when trying to use unsupported method"""
        resp = self.client.trace(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_payment_method(self):
        """It should Update an existing Payment Method"""
        # create a payment method to update
        test_payment_method = CreditCardFactory()
        test_payment_method.create()
        response = self.client.post(
            BASE_URL, json=test_payment_method.serialize(), headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the payment method
        payment_method = response.get_json()
        logging.debug(payment_method)
        payment_method["name"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{payment_method['id']}",
            json=payment_method,
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_payment = response.get_json()
        self.assertEqual(updated_payment["name"], "unknown")

    def test_update_payment_method_not_exist(self):
        """It should not Update a Payment Method that does not exist"""

        # update the payment method
        response = self.client.put(
            f"{BASE_URL}/{1001}",
            json={},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_payment_method(self):
        """It should Delete a Payment Method"""
        test_payment_method = CreditCardFactory()
        test_payment_method.create()
        response = self.client.delete(
            f"{BASE_URL}/{test_payment_method.id}",
            headers=self.headers,
        )
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
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 2)
        response = self.client.get(f"{BASE_URL}?name={second_payment_method.name}")
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], second_payment_method.serialize())

    def test_list_payment_methods_with_user_id(self):
        """It should List all PaymentMethods matching user_id query"""
        first_payment_method = CreditCardFactory()
        first_payment_method.user_id = 0
        first_payment_method.create()
        second_payment_method = CreditCardFactory()
        second_payment_method.user_id = 1
        second_payment_method.create()

        response = self.client.get(f"{BASE_URL}?user_id=1")
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], second_payment_method.serialize())

    def test_list_payment_methods_with_type(self):
        """It should List all PaymentMethods matching type query"""
        first_payment_method = CreditCardFactory()
        first_payment_method.create()
        second_payment_method = PayPalFactory()
        second_payment_method.create()

        response = self.client.get(f"{BASE_URL}?type=CREDIT_CARD")
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], first_payment_method.serialize())

        response = self.client.get(f"{BASE_URL}?type=PAYPAL")
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], second_payment_method.serialize())

    def test_list_payment_methods_multiple_queries(self):
        """It should List all PaymentMethods matching the filters"""
        first_payment_method = CreditCardFactory()
        first_payment_method.name = "a"
        first_payment_method.user_id = 11
        first_payment_method.create()
        second_payment_method = PayPalFactory()
        second_payment_method.user_id = 12
        second_payment_method.create()
        third_payment_method = CreditCardFactory()
        third_payment_method.user_id = 12
        third_payment_method.create()

        response = self.client.get(f"{BASE_URL}?type=CREDIT_CARD")
        data = response.get_json()
        self.assertEqual(len(data), 2)
        response = self.client.get(f"{BASE_URL}?type=CREDIT_CARD&user_id=12")
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], third_payment_method.serialize())

    def test_get_payment_method(self):
        """It should Get a single PaymentMethod"""
        test_payment_method = CreditCardFactory()
        test_payment_method.create()
        response = self.client.get(f"{BASE_URL}/{test_payment_method.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_payment_method.name)

    def test_set_payment_method_as_default(self):
        """It should set a payment method as the default"""
        payment_method = CreditCardFactory()
        response = self.client.post(
            BASE_URL,
            json=payment_method.serialize(),
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_method = response.get_json()
        payment_method_id = created_method["id"]

        response = self.client.put(
            f"{BASE_URL}/{payment_method_id}/set-default",
            json={"user_id": payment_method.user_id},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_method = response.get_json()
        self.assertTrue(updated_method["is_default"])

    def test_set_payment_method_as_default_no_exist(self):
        """It should set a payment method as the default"""
        response = self.client.put(
            f"{BASE_URL}/12345/set-default",
            json={"user_id": 2},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_new_default_unset_previous_default(self):
        """It should unset the previous default when a new default is set"""
        user_id = 123
        payment_method1 = CreditCardFactory(user_id=user_id)
        payment_method2 = PayPalFactory(user_id=user_id)

        resp1 = self.client.post(
            BASE_URL,
            json=payment_method1.serialize(),
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)
        method1_id = resp1.get_json()["id"]

        resp2 = self.client.post(
            BASE_URL,
            json=payment_method2.serialize(),
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(resp2.status_code, status.HTTP_201_CREATED)
        method2_id = resp2.get_json()["id"]

        response = self.client.put(
            f"{BASE_URL}/{method1_id}/set-default",
            json={"user_id": user_id},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(
            f"{BASE_URL}/{method2_id}/set-default",
            json={"user_id": user_id},
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resp1_updated = self.client.get(f"{BASE_URL}/{method1_id}")
        self.assertFalse(resp1_updated.get_json()["is_default"])

        resp2_updated = self.client.get(f"{BASE_URL}/{method2_id}")
        self.assertTrue(resp2_updated.get_json()["is_default"])

    def test_generate_apikey(self):
        """It should Generate a string of length 32"""
        self.assertEqual(len(generate_apikey()), 32)
