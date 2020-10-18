"""
Broadly used functions and classes across sonar
"""


def replace_in_file(src_file, str_to_replace, replacement_str):
    """
    Replace a string in a file and save the file back in place

    Args:
        src_file (filepath): Str or Path to a file to open
        str_to_replace (str): The string to replace
        replacement_str (str): The replacement string
    """
    with open(src_file, "r") as f:
        filedata = f.read()

    filedata = filedata.replace(str_to_replace, replacement_str)

    with open(src_file, "w") as f:
        f.write(filedata)


# https://stackoverflow.com/a/32107024
class DotDict(dict):
    """
    A dictionary that allows its members to be accessed through the dot operator
    as attributes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)
