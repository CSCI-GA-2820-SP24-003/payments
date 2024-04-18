"""
Payments Steps

Steps file for payments.feature
"""

import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


@given("the following payment methods")
def step_impl(context):
    """Delete all payment methods and load new ones"""

    # List all of the payment methods and delete them one by one
    rest_endpoint = f"{context.base_url}/api/payments"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK
    for payment_method in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{payment_method['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # load the database with new pets
    for row in context.table:
        payload = {
            "name": row["name"],
            "user_id": row["user_id"],
            "type": row["type"],
        }

        if row["type"] == "PAYPAL":
            payload["email"] = row["email"]
        else:
            payload["first_name"] = row["first_name"]
            payload["last_name"] = row["last_name"]
            payload["card_number"] = row["card_number"]
            payload["expiry_month"] = int(row["expiry_month"])
            payload["expiry_year"] = int(row["expiry_year"])
            payload["security_code"] = row["security_code"]
            payload["billing_address"] = row["billing_address"]
            payload["zip_code"] = row["zip_code"]

        context.resp = requests.post(rest_endpoint, json=payload)
        if context.resp.status_code == 400:
            print(context.resp.text)
        assert context.resp.status_code == HTTP_201_CREATED
