"""
This module defines basic object types used throughout sonar.
"""

import json


class SonarObject:
    """
    The basic object. It enforces that the object has a method to turn itself
    into a dictionary (for easy printing).
    """

    __test__ = False  # prevent pytest from picking up these objects

    def __str__(self):
        """
        Prints the object as a string

        Returns:
            str: Object as a string
        """

        return json.dumps(self.asdict())

    def asdict(self):
        """
        Placeholder function that's overridden in the child classes

        Raises:
            NotImplementedError: This function should not be called
        """

        raise NotImplementedError


class InterfacePort(SonarObject):
    """
    Used to define an interface port on a hardware module
    """

    def __init__(self, name, direction):
        """
        Initializes the parent InterfacePort class with an empty channel list

        Args:
            name (str): name of the interface
            direction (str): direction of the interface (master|slave|mixed)
        """

        self.name = name
        self.direction = direction
        self.channels = []

    def add_channel(self, name, channel_type, size=1):
        """
        Adds a channel to this interface port

        Args:
            name (str): Name of the channel signal
            channel_type (str): Type of channel
            size (int, optional): Defaults to 1. Width of channel in bits
        """

        channel = {}
        channel["name"] = name
        channel["type"] = channel_type
        channel["size"] = size
        self.channels.append(channel)

    def add_channels(self, channels):
        """
        Adds a set of channels to this interface port

        Args:
            channels (list): List of channels to add to the interface. Each
                element in the list may be a list or a dict. If it's a list,
                the name, channel_type, and (optionally) size must appear in
                this order. If it's a dict, these arguments must be keyworded.

        Raises:
            NotImplementedError: Raised on unhandled errors
        """

        for channel in channels:
            if isinstance(channel, list):
                name = channel[0]
                channel_type = channel[1]
                if len(channel) == 3:
                    size = channel[2]
                else:
                    size = 1
            elif isinstance(channel, dict):
                name = channel["name"]
                channel_type = channel["type"]
                if "size" in channel:
                    size = channel["size"]
                else:
                    size = 1
            else:
                raise NotImplementedError()
            self.add_channel(name, channel_type, size)

    def get_channel(self, channel_type):
        """
        Returns information about the named channel on this interface

        Args:
            channel_type (str): The channel type to fetch

        Raises:
            KeyError: Raised if channel_type isn't found

        Returns:
            dict: Information about the requested channel
        """

        channel_dict = None
        for channel in self.channels:
            if channel["type"] == channel_type:
                channel_dict = channel
                break
        if channel_dict is None:
            raise KeyError()
        return channel_dict

    def has_channel(self, channel_type):
        """
        Returns a boolean value if the interface has the specific channel

        Args:
            channel_type (str): The channel type to fetch

        Returns:
            boolean: True if the channel exists in the interface
        """

        channel_exists = False
        for channel in self.channels:
            if channel["type"] == channel_type:
                channel_exists = True
                break
        return channel_exists

    def asdict(self):
        """
        Converts this object to a dictionary

        Returns:
            dict: Dictionary representing this object
        """
        port = {}
        port["name"] = self.name
        port["direction"] = self.direction
        port["channels"] = self.channels
        return port
