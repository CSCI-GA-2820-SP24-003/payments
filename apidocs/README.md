# Payment Method Module Documentation

## Overview
This document provides a comprehensive overview of the Payment Method module, which includes handling of payment methods in a database using SQLAlchemy ORM and custom enumeration types for payment type validation.

## Components

### Imports and Global Variables

- **logger**: A logger object from Python's `logging` module configured to capture logs under the "flask.app" namespace.
    ```python
    logger = logging.getLogger("flask.app")
    ```

- **db**: Instance of SQLAlchemy, used to interact with the database.
    ```python
    db = SQLAlchemy()
    ```

### Custom Exceptions

#### DataValidationError
- A custom exception class that is used to handle data validation errors throughout the module.
    ```python
    class DataValidationError(Exception):
        """Used for an data validation errors"""
    ```

### Enums

#### PaymentMethodType
- An enumeration that specifies valid types of payment methods.
    ```python
    class PaymentMethodType(Enum):
        """Enumeration of valid payment types"""
        UNKNOWN = "UNKNOWN"
        CREDIT_CARD = "CREDIT_CARD"
        PAYPAL = "PAYPAL"
    ```

### Functions

#### convert_str_to_payment_method_type_enum
- A utility function to convert a string to a `PaymentMethodType` enum. Returns `None` if no matching enum is found.
    ```python
    def convert_str_to_payment_method_type_enum(value):
        """Converts a given str to PaymentMethodType enum"""
    ```

### Database Model

#### PaymentMethod
- A class representing the Payment Method resource, with fields mapped to the database table.
    ```python
    class PaymentMethod(db.Model):
        """Class that represents Payment Method resource"""
    ```

##### Attributes
- **id**: Primary key, auto-incrementing.
- **name**: A string field to store the name of the payment method.
- **user_id**: An integer field to link the payment method to a user.
- **type**: An enum field storing the payment method type.

##### Methods

###### create
- Adds a new PaymentMethod record to the database and commits the transaction.
    ```python
    def create(self):
        """Creates a PaymentMethod to the database"""
    ```

###### update
- Updates an existing PaymentMethod record in the database.
    ```python
    def update(self):
        """Updates a PaymentMethod to the database"""
    ```

###### delete
- Deletes a PaymentMethod from the database.
    ```python
    def delete(self):
        """Removes a PaymentMethod from the data store"""
    ```

###### serialize
- Converts an object instance into a dictionary format.
    ```python
    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""
    ```

###### deserialize
- Loads data from a dictionary into an object instance, effectively the reverse of serialize.
    ```python
    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""
    ```

### Class Methods

#### all
- Returns a list of all PaymentMethod records from the database.
    ```python
    @classmethod
    def all(cls):
        """Returns all of the PaymentMethod records in the database"""
    ```

#### find
- Finds a single PaymentMethod by its ID.
    ```python
    @classmethod
    def find(cls, by_id):
        """Finds PaymentMethod by its ID"""
    ```

#### find_by_name
- Finds PaymentMethod(s) by their name.
    ```python
    @classmethod
    def find_by_name(cls, name):
        """Returns all PaymentMethods with the given name"""
    ```
  
# Models for CreditCard

This document describes the `CreditCard` class and related functions within a module that handles credit card payment methods. This is part of a larger system where all payment method models are managed.

## Module Overview

The module imports several elements from the `sqlalchemy.orm` library and the `payment_method` module, facilitating operations on credit card data stored in a relational database.

### Imports

- **`validates` from `sqlalchemy.orm`**: A decorator for adding custom validation to model fields.
- **`PaymentMethod` and other related imports from `payment_method`**:
  - `PaymentMethod`: Base class for different payment methods.
  - `DataValidationError`: Exception class for handling data validation errors.
  - `PaymentMethodType`: Enumeration of payment method types.
  - `convert_str_to_payment_method_type_enum`: Utility function to convert strings to `PaymentMethodType` enum.
  - `db`: Database instance for ORM operations.

### Constants

- **`EXPIRY_MONTH_CONSTRAINTS`**: Defines valid month range for credit card expiration (1 to 12).
- **`EXPIRY_YEAR_CONSTRAINTS`**: Defines valid year range for credit card expiration (2024 to 2050).

## Class: CreditCard

`CreditCard` inherits from `PaymentMethod` and represents a credit card resource.

### Attributes

- **`id`**: Primary key, foreign key linked to `payment_method.id`.
- **`first_name`, `last_name`**: Cardholder's first and last names. Non-nullable.
- **`card_number`**: 16-digit credit card number. Non-nullable.
- **`expiry_month`, `expiry_year`**: Expiration month and year of the credit card. Non-nullable.
- **`security_code`**: 3-digit card verification value. Non-nullable.
- **`billing_address`**: Card billing address. Non-nullable.
- **`zip_code`**: 5-digit ZIP code of the billing address. Non-nullable.

### Methods

- **`serialize`**: Converts the `CreditCard` instance into a dictionary.
- **`deserialize(data)`**: Updates the `CreditCard` instance from a dictionary `data`.
- **Validation Methods**: Each field has custom validation logic defined using the `@validates` decorator.

#### Serialization and Deserialization

- `serialize`: Returns a dictionary containing all the credit card details.
- `deserialize(data)`: Accepts a dictionary `data` and updates the `CreditCard` instance. Raises `DataValidationError` if necessary attributes are missing or data types are incorrect.

### Validations

Each field has custom validation methods:
- **`validate_first_name`**, **`validate_last_name`**: Ensure names contain only letters.
- **`validate_card_number`**: Ensures the card number is numeric and exactly 16 digits long.
- **`validate_security_code`**: Checks that the security code is numeric and exactly 3 digits long.
- **`validate_expiry_month`**, **`validate_expiry_year`**: Validates that the expiration date falls within the specified constraints.
- **`validate_zip_code`**: Ensures the ZIP code is numeric and exactly 5 digits long.

## Utility Functions

- **`is_not_int(value)`**: Returns `True` if `value` is not an integer.
- **`is_not_str(value)`**: Returns `True` if `value` is not a string.

These functions support the validation methods in the `CreditCard` class by checking data types before validating content.

# PayPal Class Documentation

The `PayPal` class extends the `PaymentMethod` class and represents a PayPal payment method in a payment system. This class is responsible for handling the serialization and deserialization of PayPal specific data and ensuring the validity of the email associated with the PayPal account.

## Attributes

### `id`
- **Type**: `db.Integer`
- **Description**: The primary key for the PayPal record, which also serves as a foreign key linking to the primary key of the `payment_method` table.
- **Details**:
  - This field is linked via a foreign key constraint to the `payment_method.id` field.
  - On deletion of the linked payment method, corresponding PayPal entries are also deleted (`ondelete="CASCADE"`).

### `email`
- **Type**: `db.String`
- **Description**: Stores the email address associated with the PayPal account.
- **Constraints**:
  - This field cannot be null (`nullable=False`).

### `__mapper_args__`
- **Type**: `dictionary`
- **Description**: Used to configure options for the mapper. Specifies that instances of `PayPal` have a specific polymorphic identity.
- **Details**:
  - `polymorphic_identity`: Set to `PaymentMethodType.PAYPAL` to differentiate PayPal payment methods from other types.

## Methods

### `serialize()`
- **Returns**: `dict`
- **Description**: Converts a `PayPal` instance into a dictionary format, suitable for JSON serialization.
- **Output**:
  - The method returns a dictionary with keys such as `id`, `name`, `type`, `user_id`, and `email`, representing the properties of the PayPal object.

### `deserialize(data)`
- **Parameters**:
  - `data` (dict): A dictionary containing the PayPal-specific data.
- **Description**: Populates the attributes of a `PayPal` instance based on the dictionary input.
- **Exceptions**:
  - Raises `DataValidationError` if any necessary attributes are missing or if the data type is incorrect.
- **Return**: Returns the updated instance itself.

### `validate_email(_key, email)`
- **Parameters**:
  - `_key`: The attribute name being validated (unused in the method body).
  - `email`: The email address to validate.
- **Description**: Validates the `email` field to ensure it contains a valid email address format.
- **Return**:
  - Returns the email if valid.
  - Raises `DataValidationError` if the email is not valid.

## Validations

- The `email` attribute of the `PayPal` class is validated using the `validate_email` method, ensuring that any email set to a `PayPal` instance is in the correct format.

## Helper Functions

### `is_valid_email(email)`
- **Parameters**:
  - `email`: Email address to validate.
- **Returns**: `bool`
- **Description**: Checks if the provided email address is in a valid format using a regular expression.
- **Details**:
  - This function utilizes the regular expression to match typical email patterns and returns `True` if the email is valid, otherwise `False`.
