"""
Models for PaymentMethod

All of the models are stored in this module
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class FieldValidationError(Exception):
    """Used for field validation errors when creating a resource"""


class PaymentType(Enum):
    """Enumeration of valid payment types"""

    UNKNOWN = 0
    CREDIT_CARD = 1
    PAYPAL = 2


EXPIRY_MONTH_CONSTRAINTS = [1, 12]
EXPIRY_YEAR_CONSTRAINTS = [2024, 2050]


class PaymentMethod(db.Model):
    """
    Class that represents a PaymentMethod
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    payment_type = db.Column(
        db.Enum(PaymentType), nullable=False, server_default=(PaymentType.UNKNOWN.name)
    )
    payment_type_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<PaymentMethod {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a PaymentMethod to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        logger.debug(self.id)
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a PaymentMethod to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a PaymentMethod from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a PaymentMethod into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "payment_type": self.payment_type.name,
            "payment_type_id": self.payment_type_id,
            "user_id": self.user_id,
        }

    def deserialize(self, data):
        """
        Deserializes a PaymentMethod from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.payment_type_id = data["payment_type_id"]
            self.payment_type = getattr(
                PaymentType, data["payment_type"]
            )  # create enum from string
            self.user_id = data["user_id"]
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid PaymentMethod: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid PaymentMethod: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the PaymentMethods in the database"""
        logger.info("Processing all PaymentMethods")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a PaymentMethod by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all PaymentMethods with the given name

        Args:
            name (string): the name of the PaymentMethods you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)


class CreditCard(db.Model):
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

    def create(self):
        """
        Adds a CreditCard to the database
        """
        logger.info(
            "Creating credit card with last four digits %s", self.card_number[-4:]
        )
        self.id = None  # pylint: disable=invalid-name
        logger.debug(self.id)
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a CreditCard from the data store"""
        logger.info("Deleting record: %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

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
    # CLASS METHODS
    ##################################################

    @classmethod
    def find(cls, by_id):
        """Finds a CreditCard by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

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
