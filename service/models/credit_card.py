"""
Models for PaymentMethod

All of the models are stored in this module
"""

from sqlalchemy.orm import validates
from .persistent_base import PersistentBase, DataValidationError, db


class FieldValidationError(Exception):
    """Used for field validation errors when creating a resource"""


EXPIRY_MONTH_CONSTRAINTS = [1, 12]
EXPIRY_YEAR_CONSTRAINTS = [2024, 2050]


class CreditCard(db.Model, PersistentBase):
    """
    Class that represents a CreditCard type
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    payment_method_id = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    card_number = db.Column(db.String(16), nullable=False)
    expiry_month = db.Column(
        db.Integer,
        nullable=False,
    )
    expiry_year = db.Column(
        db.Integer,
        nullable=False,
    )
    security_code = db.Column(db.String(3), nullable=False)
    billing_address = db.Column(db.Text, nullable=False)
    zip_code = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f"<CreditCard **** **** **** {self.card_number[-4:]} id=[{self.id}]>"

    def serialize(self):
        """Serializes a PaymentMethod into a dictionary"""
        return {
            "id": self.id,
            "payment_method_id": self.payment_method_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "card_number": self.card_number,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "security_code": self.security_code,
            "billing_address": self.billing_address,
            "zip_code": self.zip_code,
        }

    def deserialize(self, data):
        """
        Deserializes a PaymentMethod from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.payment_method_id = data["payment_method_id"]
            self.first_name = data["first_name"]
            self.last_name = data["last_name"]
            self.card_number = data["card_number"]
            self.expiry_month = data["expiry_month"]
            self.expiry_year = data["expiry_year"]
            self.security_code = data["security_code"]
            self.billing_address = data["billing_address"]
            self.zip_code = data["zip_code"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid CreditCard: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid CreditCard: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # VALIDATIONS
    ##################################################

    @validates("first_name")
    def validate_first_name(self, _key, first_name):
        """Validates `first_name` field"""
        if not first_name.isalpha():
            raise FieldValidationError("First name field must contain letters only")

        return first_name

    @validates("last_name")
    def validate_last_name(self, _key, last_name):
        """Validates `last_name` field"""
        if not last_name.isalpha():
            raise FieldValidationError("Last name field must contain letters only")

        return last_name

    @validates("card_number")
    def validate_card_number(self, _key, card_number):
        """Validates `card_number` field"""
        if not card_number.isdigit():
            raise FieldValidationError("Card number field must be numeric")

        if not len(card_number) == 16:
            raise FieldValidationError("Card number field must be 16 digits")

        return card_number

    @validates("security_code")
    def validate_security_code(self, _key, security_code):
        """Validates `security_code` field"""
        if not security_code.isdigit():
            raise FieldValidationError("Security code field must be numeric")

        if not len(security_code) == 3:
            raise FieldValidationError("Security code field must be 3 digits")

        return security_code

    @validates("expiry_year")
    def validate_expiry_year(self, _key, expiry_year):
        """Validates `expiry_year` field"""
        if expiry_year < 2024 or expiry_year > 2050:
            raise FieldValidationError("Expiry year field is invalid")

        return expiry_year

    @validates("expiry_month")
    def validate_expiry_month(self, _key, expiry_month):
        """Validates `expiry_month` field"""
        if expiry_month < 1 or expiry_month > 12:
            raise FieldValidationError("Expiry month field is invalid")

        return expiry_month

    @validates("zip_code")
    def validate_zip_code(self, _key, zip_code):
        """Validates `zip_code` field"""
        if not zip_code.isdigit():
            raise FieldValidationError("ZIP code field must be numeric")

        if not len(zip_code) == 5:
            raise FieldValidationError("ZIP code field must be 3 digits")

        return zip_code
