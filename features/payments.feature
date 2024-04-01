Feature: The payments service back-end
    As an e-commerce platform owner
    I need a RESTful service for payments
    So that my platform's users can create payment methods

Background:
    Given the following payment methods
        | name        | user_id | type        | email             | first_name | last_name | card_number      | expiry_month | expiry_year | security_code | billing_address | zip_code |
        | best method | 1       | PAYPAL      | testmail@mail.com |            |           |                  |              |             |               |                 |          |
        | do not use  | 90      | PAYPAL      | john.doe@mail.com |            |           |                  |              |             |               |                 |          |
        | secondary   | 1130    | PAYPAL      | jane.doe@mail.com |            |           |                  |              |             |               |                 |          |
        | abc         | 1       | CREDIT_CARD |                   | john       | doe       | 1234123412341234 | 11           | 2027        | 123           | 90 W East St    | 10001    |
        | efg         | 1       | CREDIT_CARD |                   | john       | doe       | 3456345634563456 | 06           | 2026        | 999           | 10 W East St    | 10003    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Payments" in the title
    And I should not see "404 Not Found"

Scenario: List all payments
    When I visit the "Home Page"
    And I press the "Search Payment Methods" button
    Then I should see "best method" in the results
    And I should see "do not use" in the results
    And I should see "secondary" in the results
    And I should see "abc" in the results
    And I should see "efg" in the results
