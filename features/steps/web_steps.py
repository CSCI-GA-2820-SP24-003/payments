"""
Web Steps

Steps file for web interactions with Selenium framework
"""
# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


ID_PREFIX = "payments_"

@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)

@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the title for a message"""
    assert message in context.driver.title

@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, 'body')
    assert text_string not in element.text

@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(" ", "-")
    context.driver.find_element(By.ID, button_id).click()

@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, 'results-body'),
            name
        )
    )
    assert found
