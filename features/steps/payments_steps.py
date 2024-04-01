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

@given('the following payment methods')
def step_impl(context):
    """ Delete all payment methods and load new ones """

    # List all of the payment methods and delete them one by one
    rest_endpoint = f"{context.base_url}/payments"
    context.resp = requests.get(rest_endpoint)
    assert context.resp.status_code == HTTP_200_OK
    for payment_method in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{payment_method['id']}")
        assert context.resp.status_code == HTTP_204_NO_CONTENT

    # load the database with new pets
    for row in context.table:
        payload = {
            "name": row['name'],
            "user_id": row['user_id'],
            "type": row['type'],
            "email": row['email'],
            "first_name": row['first_name'],
            "last_name": row['last_name'],
            "card_number": row['card_number'],
            "expiry_month": row['expiry_month'],
            "expiry_year": row['expiry_year'],
            "security_code": row['security_code'],
            "billing_address": row['billing_address'],
            "zip_code": row['zip_code'],
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert context.resp.status_code == HTTP_201_CREATED
