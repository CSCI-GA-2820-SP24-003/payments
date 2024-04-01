"""
Web Steps

Steps file for web interactions with Selenium framework
"""
# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
from behave import when, then

ID_PREFIX = "payments_"

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)
