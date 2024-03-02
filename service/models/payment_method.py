"""
Models for PaymentMethod

All of the models are stored in this module
"""

import logging
from enum import Enum
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PaymentMethodType(Enum):
    """Enumeration of valid payment types"""

    CREDIT_CARD = 1
    PAYPAL = 2


class PaymentMethod(db.Model):
    """Class that represents Payment Method resource"""

    ##################################################
    # TABLE SCHEMA
    ##################################################

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Enum(PaymentMethodType), nullable=False)

    # https://docs.sqlalchemy.org/en/20/orm/inheritance.html
    #
    # We are utilizing the SQLAlchemy inheritance hierarchy with polymorphic identities
    # This allows us to query all payment methods from PaymentMethod class
    __mapper_args__ = {
        "polymorphic_on": "type",
    }

    def __repr__(self):
        return f"<PaymentMethod {self.name} id=[{self.id}]>"

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self) -> None:
        """
        Creates a PaymentMethod to the database
        """
        logger.info("Creating %s", self)
        # id must be none to generate next primary key
        self.id = None
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating PaymentMethod record: %s", self)
            raise DataValidationError(e) from e

    def update(self) -> None:
        """
        Updates a PaymentMethod to the database
        """
        logger.info("Updating %s", self)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self) -> None:
        """Removes a PaymentMethod from the data store"""
        logger.info("Deleting %s", self)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting PaymentMethod: %s", self)
            raise DataValidationError(e) from e

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the PaymentMethod records in the database"""
        logger.info("Processing all records")
        # pylint: disable=no-member
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds PaymentMethod by its ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        # pylint: disable=no-member
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all PaymentMethods with the given name

        Args:
            name (string): the name of the PaymentMethods you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
