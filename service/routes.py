######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
######################################################################

"""
Payments Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Payments from the inventory of payments in the PaymentShop
"""

from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from resource import error

from service.models import PaymentMethod
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for root URL")
    return (
        jsonify(
            name="Payments service",
            version="1.0",
            status=status.HTTP_200_OK,
            methods=list(
                [
                    {
                        "path": "/payment-methods",
                        "method": "GET",
                        "operation": "Read",
                        "description": "List all payment methods for a user",
                        "request_body": "None",
                        "response_body": "Payment method records",
                    },
                    {
                        "path": "/payment-method/:id",
                        "method": "GET",
                        "operation": "Read",
                        "description": "Provide detailed information about an existing payment method",
                        "request_body": "None",
                        "response_body": "Payment method record",
                    },
                    {
                        "path": "/payment-method",
                        "method": "POST",
                        "operation": "Create",
                        "description": "Create a payment method",
                        "request_body": "Payment method record",
                        "response_body": "None",
                    },
                    {
                        "path": "/payment-method/:id",
                        "method": "PUT",
                        "operation": "Update",
                        "description": "Update a given payment method",
                        "request_body": "Payment method record",
                        "response_body": "None",
                    },
                    {
                        "path": "/payment-method/:id",
                        "method": "DELETE",
                        "operation": "Delete",
                        "description": "Delete a given payment method",
                        "request_body": "None",
                        "response_body": "None",
                    },
                ]
            ),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...


######################################################################
# DELETE A PAYMENT METHOD
######################################################################
@app.route("/payment-method/<int:id>", methods=["DELETE"])
def delete_payment_method(id):
    """
    Delete a Payment Method

    This endpoint will delete a Payment Method based the id specified in the path
    """
    app.logger.info("Request to delete payment with id: %d", id)

    payment = PaymentMethod.find(id)
    if payment:
        payment.delete()

    app.logger.info("Payment with ID: %d delete complete.", id)
    return "", status.HTTP_204_NO_CONTENT

def list_payments_method():
    """Returns all of the Payments"""
    app.logger.info("Request for payment list")

    payment = []

    # See if any query filters were passed in
    category = request.args.get("category")
    name = request.args.get("name")
    if category:
        payment = PaymentMethod.find_by_category(category)
    elif name:
        payment = PaymentMethod.find_by_name(name)
    else:
        payment = PaymentMethod.all()

    results = [payment.serialize() for i in payment]
    app.logger.info("Returning %d payments", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/payment-method/<int:id>", methods=["GET"])
def get_payment_method(id):
    """
    Retrieve a single Payment

    This endpoint will return a Payment based on it's id
    """
    app.logger.info("Request for payment with id: %s", id)

    payment = PaymentMethod.find(id)
    if not payment:
        error(status.HTTP_404_NOT_FOUND, f"Payment with id '{id}' was not found.")

    app.logger.info("Returning payment: %s", payment.name)
    return jsonify(payment.serialize()), status.HTTP_200_OK
