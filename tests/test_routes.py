"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, PaymentMethod
from .factories import PaymentMethodFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/payment-method"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestPaymentService(TestCase):
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

    # Todo: Add your test cases here...
    def test_update_payment(self):
        """It should Update an existing Pet"""
        # create a payment to update
        test_payment = PaymentMethodFactory()
        response = self.client.post(BASE_URL, json=test_payment.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the payment
        new_payment = response.get_json()
        logging.debug(new_payment)
        new_payment["category"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_payment['id']}", json=new_payment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_payment = response.get_json()
        self.assertEqual(updated_payment["category"], "unknown")
