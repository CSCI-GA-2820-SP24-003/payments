"""
Model for PayPal
"""

import re
from sqlalchemy.orm import validates
from .payment_method import (
    PaymentMethod,
    DataValidationError,
    PaymentMethodType,
    convert_str_to_payment_method_type_enum,
    db,
)


class PayPal(PaymentMethod):
    """
    Class that represents PayPal resource
    """

    ##################################################
    # TABLE SCHEMA
    ##################################################

    id = db.Column(
        db.Integer,
        db.ForeignKey("payment_method.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email = db.Column(db.String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": PaymentMethodType.PAYPAL}

    def serialize(self):
        """Serializes a PayPal into a dictionary"""
        return {  # pylint: disable=duplicate-code
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "user_id": self.user_id,
            "email": self.email,
            "is_default": self.is_default,
        }

    def deserialize(self, data):
        """
        Deserializes a PayPal from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.type = convert_str_to_payment_method_type_enum(data["type"])
            self.user_id = data["user_id"]
            self.email = data["email"]
            self.is_default = data.get("is_default", False)
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid PayPal: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid PayPal: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # VALIDATIONS
    ##################################################

    @validates("email")
    def validate_email(self, _key, email):
        """Validates `email` field"""
        if not is_valid_email(email):
            raise DataValidationError("Email field is invalid")
        return email


def is_valid_email(email):
    """Checks whether its valid email"""
    return (
        re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email)
        is not None
    )
