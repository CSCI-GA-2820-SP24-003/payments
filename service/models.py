"""
Models for PaymentMethod

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PaymentType(Enum):
    """Enumeration of valid payment types"""

    UNKNOWN = 0
    CREDIT_CARD = 1
    PAYPAL = 2


class PaymentMethod(db.Model):
    """
    Class that represents a PaymentMethod
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
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
