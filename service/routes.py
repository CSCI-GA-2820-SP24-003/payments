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
Payment Store Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Payments from the inventory of payments in the PaymentShop
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import YourResourceModel
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# UPDATE AN EXISTING Payment
######################################################################
@app.route("/payments/<int:payment_id>", methods=["PUT"])
def update_payments(payment_id):
    """
    Update a Payment

    This endpoint will update a Payment based the body that is posted
    """
    app.logger.info("Request to update payment with id: %d", payment_id)
    check_content_type("application/json")

    payment = payment.find(payment_id)
    if not payment:
        error(
            status.HTTP_404_NOT_FOUND, f"Payment with id: '{payment_id}' was not found."
        )

    payment.deserialize(request.get_json())
    payment.id = payment_id
    payment.update()

    app.logger.info("Payment with ID: %d updated.", payment.id)
    return jsonify(payment.serialize()), status.HTTP_200_OK


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
