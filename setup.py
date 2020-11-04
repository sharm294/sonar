"""
Python build script for setuptools

Raises:
    RuntimeError: Raised if __version__ information is not found
"""

import codecs
import os

from setuptools import find_packages, setup


def get_version(filepath):
    """
    Extracts the version string from a file

    Args:
        filepath (str): Path to the file to search for the version

    Raises:
        RuntimeError: Raised if __version__ not found

    Returns:
        str: Version of the project
    """
    for line in read(filepath).splitlines():
        if line.startswith("__version__"):
            return line.split('"')[1]
    raise RuntimeError("Unable to find version string.")


def read(filepath):
    """
    Reads the file at the filepath

    Args:
        filepath (str): Path to the file to read

    Returns:
        str: File contents as a string
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, filepath), encoding="utf-8") as f:
        return f.read()


setup(
    name="sonar",
    version=get_version("sonar/__init__.py"),
    author="Varun Sharma",
    author_email="varuns.sharma@mail.utoronto.ca",
    packages=find_packages(),
    description=("Manage and test hardware and mixed language projects"),
    long_description=read("README.rst"),
    long_description_content_type="text/markdown",
    url="https://github.com/sharm294/sonar",
    license="License :: OSI Approved :: MIT License",
    platforms="linux",
    install_requires=["toml"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.7",
    # this doesn't work to enable argcomplete
    # entry_points={"console_scripts": ["sonar=sonar.main:main"]},
    scripts=["tools/sonar"],
    include_package_data=True,
)
