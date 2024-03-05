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
from service.common import status  # HTTP Status Codes
from service.models import PaymentMethod, PaymentMethodType, CreditCard, PayPal


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
######################################################################
# UPDATE AN EXISTING PAYMENT METHOD
######################################################################
@app.route("/payments/<int:payment_method_id>", methods=["PUT"])
def update_payment_method(payment_method_id):
    """
    Update a PaymentMethod

    This endpoint will update a PaymentMethod based the body that is posted
    """
    app.logger.info("Request to update payment with id: %d", payment_method_id)
    check_content_type("application/json")

    payment = PaymentMethod.find(payment_method_id)
    if not payment:
        error(
            status.HTTP_404_NOT_FOUND,
            f"PaymentMethod with id: '{payment_method_id}' was not found.",
        )

    payment.deserialize(request.get_json())
    payment.id = payment_method_id
    payment.update()

    app.logger.info("PaymentMethod with ID: %d updated.", payment.id)
    return jsonify(payment.serialize()), status.HTTP_200_OK


######################################################################
#  CREATE A PAYMENT METHOD
######################################################################
@app.route("/payment-method", methods=["POST"])
def create_payment_method():
    """
    Creates Payment Method
    This endpoint will create a PaymentMethod based on the data in the body that is posted
    """
    app.logger.info("Request to create a PaymentMethod")
    check_content_type("application/json")
    body = request.get_json()
    payment_method = None
    method_type = body.get("type")

    if method_type == PaymentMethodType.CREDIT_CARD.value:
        payment_method = CreditCard()

    if method_type == PaymentMethodType.PAYPAL.value:
        payment_method = PayPal()

    # Abort if no type was provided
    if payment_method is None:
        abort(status.HTTP_400_BAD_REQUEST, "PaymentMethod must have a type")

    payment_method.deserialize(body)
    payment_method.create()
    message = payment_method.serialize()

    return jsonify(message), status.HTTP_201_CREATED


######################################################################
# DELETE A PAYMENT METHOD
######################################################################
@app.route("/payment-method/<int:payment_method_id>", methods=["DELETE"])
def delete_payment_method(payment_method_id):
    """
    Delete a Payment Method

    This endpoint will delete a PaymentMethod based the id specified in the path
    """
    app.logger.info("Request to delete payment with id: %d", payment_method_id)

    payment_method = PaymentMethod.find(payment_method_id)
    if payment_method:
        payment_method.delete()

    app.logger.info("Payment with ID: %d delete complete.", payment_method_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )



######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
    
@app.route("/payment-methods", methods=["GET"])
def list_payment_methods():
    """Returns all of the PaymentMethods"""
    app.logger.info("Request for payment method list")

    payment_methods = []

    # See if any query filters were passed in
    name = request.args.get("name")
    if name:
        payment_methods = PaymentMethod.find_by_name(name)
    else:
        payment_methods = PaymentMethod.all()

    results = [payment_method.serialize() for payment_method in payment_methods]
    app.logger.info("Returning %d payment methods", len(results))
    return jsonify(results), status.HTTP_200_OK


@app.route("/payment-method/<int:payment_method_id>", methods=["GET"])
def get_payment_method(payment_method_id):
    """
    Retrieve a single PaymentMethod

    This endpoint will return a PaymentMethod based on its ID
    """
    app.logger.info("Request for payment with id: %s", payment_method_id)

    payment_method = PaymentMethod.find(payment_method_id)
    if not payment_method:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"PaymentMethod with id '{payment_method_id}' was not found.",
        )

    app.logger.info("Returning PaymentMethod: %s", payment_method.name)
    return jsonify(payment_method.serialize()), status.HTTP_200_OK

