"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase

from tests.factories import PaymentMethodFactory, PayPalFactory
from wsgi import app
from service.common import status
from service.models import db, PaymentMethod

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/payment-method"


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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

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


    def _create_payments(self, count):
        """Factory method to create payments in bulk"""
        payments = []
        for _ in range(count):
            test_payment = PayPalFactory()
            # response = self.client.post(BASE_URL, json=test_payment.serialize())
            # self.assertEqual(
            #     response.status_code,
            #     status.HTTP_201_CREATED,
            #     "Could not create test payment",
            # )
            # new_payment = response.get_json()
            # test_payment.id = new_payment[1]
            test_payment.create()
            payments.append(test_payment)

        return payments

    def test_delete_payment(self):
        """It should Delete a Payment Method"""
        test_payment = self._create_payments(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_payment.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_payment.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_payment(self):
        """It should List all Payment Method"""
        self._create_payments(1)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)

    def test_get_payment(self):
        """It should Get a single Payment"""
        test_payment = self._create_payments(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_payment.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_payment.name)











