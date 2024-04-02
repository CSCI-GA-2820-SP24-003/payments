"""
Web Steps

Steps file for web interactions with Selenium framework
"""

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
import logging
from behave import when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions


ID_PREFIX = "payments_"


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(" ", "-")
    context.driver.find_element(By.ID, button_id).click()


@then('I should see "{name}" in the results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element((By.ID, "results-body"), name)
    )
    assert found


@when('I set the "{element_name}" to "{value}"')
def step_impl(context, element_name, value):
    element_id = element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(value)


@then('I should see the "{notification_type}" notification')
def step_impl(context, notification_type):
    css_selector_name = f"div.notification.{notification_type.lower()}"
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located(
            (By.CSS_SELECTOR, css_selector_name)
        )
    )
    assert found


@when('I copy the "{element_name}"')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(" ", "-")
    element = context.driver.find_element(By.ID, element_id)
    context.clipboard = element.text
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste to "{element_name}"')
def step_impl(context, element_name):
    element_id = element_name.lower().replace(" ", "-")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = element_name.lower()
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@when('I press on edit "{name}"')
def step_impl(context, name):
    element_id = name.lower().replace(" ", "-") + "-id"
    result_id = context.driver.find_element(By.ID, element_id).text
    button_id = f"edit-result-{result_id}"
    context.driver.find_element(By.ID, button_id).click()
