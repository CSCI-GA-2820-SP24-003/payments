"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, PaymentMethod


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/payments"

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    

    def test_update_payment(self):
        """It should Update an existing Payment"""
        # create a payment to update
        test_payment = PaymentFactory()
        response = self.client.post(BASE_URL, json=test_payment.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the payment
        new_payment = response.get_json()
        logging.debug(new_payment)
        new_payment["name"] = test_payment.name
        response = self.client.put(f"{BASE_URL}/{new_payment['id']}", json=new_payment)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_payment = response.get_json()
        self.assertEqual(updated_payment["name"], test_payment.name)
        
        """It should call the home page and receive information about existing methods"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        methods = data["methods"]
        self.assertEqual(data["status"], status.HTTP_200_OK)
        self.assertEqual(data["name"], "Payments service")
        self.assertEqual(data["version"], "1.0")
        self.assertEqual(len(methods), 5)

       
