from setuptools import setup, find_packages
import os
import codecs


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            # __version__ = "0.9"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def read(filepath):
    here = os.path.abspath(os.path.dirname(__file__))
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, filepath), encoding="utf-8") as fp:
        return fp.read()


setup(
    name="sonar",
    version=get_version("src/__init__.py"),
    author="Varun Sharma",
    author_email="varuns.sharma@mail.utoronto.ca",
    packages=find_packages(where="src"),
    description=("Manage and test hardware and mixed language projects"),
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/sharm294/sonar",
    license="License :: OSI Approved :: MIT License",
    platforms="linux",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.6",
    # scripts=["tools/excode"],
)
