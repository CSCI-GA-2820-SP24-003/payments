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
# pylint: disable=redefined-builtin, cyclic-import
import secrets
from flask import jsonify, request, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse
from service.common import status  # HTTP Status Codes
from service.models import PaymentMethod, PaymentMethodType, CreditCard, PayPal
from . import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for root URL")
    return app.send_static_file("index.html")


######################################################################
# Configure the Root route before OpenAPI
######################################################################

# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "CreateModel",
    {
        "name": fields.String(
            required=True, description="The name of the PaymentMethod"
        ),
        "is_default": fields.Boolean(
            required=True, description="Is the PaymentMethod set as default?"
        ),
        # pylint: disable=protected-access
        "type": fields.String(
            required=True,
            # discriminator=True,
            enum=PaymentMethodType._member_names_,
            description="The type of PaymentMethod",
        ),
        "user_id": fields.Integer(
            required=True, description="The user_id of the relevant user"
        ),
    },
)

payment_method_model = api.inherit(
    "PaymentMethodModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)
credit_card_model = api.inherit(
    "CreditCardModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "first_name": fields.String(required=True),
        "last_name": fields.String(required=True),
        "card_number": fields.String(required=True),
        "expiry_month": fields.Integer(required=True),
        "expiry_year": fields.Integer(required=True),
        "security_code": fields.String(required=True),
        "billing_address": fields.String(required=True),
        "zip_code": fields.String(required=True),
    },
)

paypal_model = api.inherit(
    "PaypalModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
        "email": fields.String(
            description="The email associated with a paypal account"
        ),
    },
)

# query string arguments
payment_args = reqparse.RequestParser()
payment_args.add_argument(
    "name", type=str, location="args", required=False, help="List Payments by name"
)
payment_args.add_argument(
    "type", type=str, location="args", required=False, help="List Payments by type"
)
payment_args.add_argument(
    "user_id",
    type=str,
    location="args",
    required=False,
    help="List Payments by user_id",
)


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
# GET HEALTH
######################################################################
@app.route("/health")
def get_health():
    """Check whether service is running"""
    return jsonify(status="OK"), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /payments/{id}
######################################################################
@api.route("/payments/<payment_method_id>")
@api.param("payment_method_id", "The PaymentMethod identifier")
class PaymentResource(Resource):
    """
    PaymentResource class

    Allows the manipulation of a single Payment method
    GET /payment/{id} - Returns a Payment with the id
    PUT /payment/{id} - Update a Payment with the id
    DELETE /payment/{id} -  Deletes a Payment with the id
    """

    ######################################################################
    # GET A PAYMENT METHOD
    ######################################################################
    @api.doc("get_payments")
    @api.response(404, "PaymentMethod not found")
    # @api.marshal_with(paymentmethod_model)
    def get(self, payment_method_id):
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
        return payment_method.serialize(), status.HTTP_200_OK

    ######################################################################
    # UPDATE AN EXISTING PAYMENT METHOD
    ######################################################################
    @api.doc("update_payments", security="apikey")
    @api.response(404, "PaymentMethod not found")
    @api.response(400, "The posted PaymentMethod data was not valid")
    def put(self, payment_method_id):
        """
        Update a PaymentMethod

        This endpoint will update a PaymentMethod based the body that is posted
        """
        app.logger.info(
            f"Request to update payment with id: {payment_method_id}",
        )
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
        return payment.serialize(), status.HTTP_200_OK

    ######################################################################
    # DELETE A PAYMENT METHOD
    ######################################################################
    @api.doc("delete_payments", security="apikey")
    @api.response(204, "PaymentMethod deleted")
    def delete(self, payment_method_id):
        """
        Delete a Payment Method

        This endpoint will delete a PaymentMethod based the id specified in the path
        """
        app.logger.info(f"Request to delete payment with id: {payment_method_id}")

        payment_method = PaymentMethod.find(payment_method_id)
        if payment_method:
            payment_method.delete()

        app.logger.info(f"Payment with ID: {payment_method_id} delete complete.")
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /payments
######################################################################
@api.route("/payments", strict_slashes=False)
class PaymentCollection(Resource):
    """Handles all interactions with collections of PaymentMethods"""

    ######################################################################
    # LIST PAYMENT METHODS
    ######################################################################
    @api.doc("list_payments")
    @api.expect(payment_args, validate=True)
    def get(self):
        """Returns all of the PaymentMethods"""
        app.logger.info("Request for payment method list")

        # See if any query filters were passed in
        args = payment_args.parse_args()
        name = args["name"]
        payment_type = args["type"]
        user_id = args["user_id"]
        q = PaymentMethod.query
        if name:
            q = PaymentMethod.find_by_name(name, q)
        if payment_type:
            q = PaymentMethod.find_by_type(payment_type.upper(), q)
        if user_id:
            q = PaymentMethod.find_by_user_id(int(user_id), q)

        results = [payment_method.serialize() for payment_method in q.all()]
        app.logger.info("Returning %d payment methods", len(results))
        return results, status.HTTP_200_OK

    ######################################################################
    #  CREATE A PAYMENT METHOD
    ######################################################################
    @api.doc("create_payments", security="apikey")
    @api.response(400, "The posted data was not valid")
    def post(self):
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
        location_url = api.url_for(
            PaymentResource, payment_method_id=payment_method.id, _external=True
        )
        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################
# SET DEFAULT PAYMENT METHOD
######################################################
@api.route("/payments/<payment_method_id>/set-default")
@api.param("payment_method_id", "The PaymentMethod identifier")
class SetDefaultResource(Resource):
    """Set default actions on a PaymentMethod"""

    @api.doc("set_default_payments")
    @api.response(404, "PaymentMethod not found")
    @api.response(409, "The PaymentMethod cannot be set as default")
    def put(self, payment_method_id):
        """
        Set a payment method as default.

        This endpoint will mark a given payment method as the default one
        and unset the is_default flag for all other payment methods for the same user
        """
        app.logger.info(f"Setting payment method {payment_method_id} as default")

        payment_method = PaymentMethod.find(payment_method_id)
        if not payment_method:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"PaymentMethod with id '{payment_method_id}' was not found",
            )

        payment_method.set_default_for_user()

        app.logger.info(f"Payment method {payment_method_id} set as default")
        return payment_method.serialize(), status.HTTP_200_OK


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


def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
