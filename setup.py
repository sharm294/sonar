from setuptools import setup, find_packages
import os
import codecs


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            return line.split('"')[1]
    else:
        raise RuntimeError("Unable to find version string.")


def read(filepath):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, filepath), encoding="utf-8") as fp:
        return fp.read()


setup(
    name="sonar",
    version=get_version("sonar/__init__.py"),
    author="Varun Sharma",
    author_email="varuns.sharma@mail.utoronto.ca",
    packages=find_packages(),
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
    # this doesn't work to enable argcomplete
    # entry_points={"console_scripts": ["sonar=sonar.main:main"]},
    scripts=["tools/sonar"],
    include_package_data=True,
)
