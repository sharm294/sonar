"""
Defines the base classes for all layers
"""

from typing import Dict

from sonar.base_types import SonarObject


class Layer(SonarObject):
    """
    Base class for all layers
    """

    def __init__(self, name):
        # self.root_layer = None
        self.name = name
        self.fields: Dict[str, Field] = {}
        self.payload = None

    def add_field(self, name, field):
        """
        Add a field to this layer as part of its header

        Args:
            name (str): Name of the field
            field (Field): The field object
        """
        self.fields[name] = field

    def get_field(self, name):
        """
        Retrieve a field from this layer

        Args:
            name (str): Name of the field

        Returns:
            Field: The field object
        """
        return self.fields[name]

    def add_payload(self, payload):
        """
        Add payload to this layer. This may be bytes or another Layer

        Args:
            payload (bytes or Layer): Data to add as payload
        """
        self.payload = payload

    def asdict(self):
        tmp = {"name": self.name}
        tmp["fields"] = {k: v.asdict() for k, v in self.fields.items()}
        if self.payload is not None:
            if isinstance(self.payload, Layer):
                tmp["payload"] = self.payload.asdict()
            else:
                tmp["payload"] = self.payload
        return tmp


class Field(SonarObject):
    """
    Fields make up the headers of each layer
    """

    def __init__(self, name, value):
        self.value = value
        self.name = name

    def to_bytes(self):
        """
        Get the field value as bytes

        Returns:
            bytes: Value of the field
        """
        return self.value

    def asdict(self):
        return {"value": self.value}
