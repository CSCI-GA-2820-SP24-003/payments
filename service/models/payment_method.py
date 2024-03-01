"""
Models for PaymentMethod

All of the models are stored in this module
"""

from enum import Enum
from .persistent_base import PersistentBase, DataValidationError, db, logger


class PaymentType(Enum):
    """Enumeration of valid payment types"""

    UNKNOWN = 0
    CREDIT_CARD = 1
    PAYPAL = 2


class PaymentMethod(db.Model, PersistentBase):
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
    def find_by_name(cls, name):
        """Returns all PaymentMethods with the given name

        Args:
            name (string): the name of the PaymentMethods you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
