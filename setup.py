import os
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

def read(file_name: str):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

def readlines(file_name: str):
    return open(os.path.join(os.path.dirname(__file__), file_name)).readlines()

setup(
    author="Georg Kasper",
    description="A decorator to unify logging, metrics and notifications.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    name="atl-observe",
    packages=find_packages(),
    url="https://github.com/atlassian-labs/observe",
    version=read('version'),
    install_requires=readlines('requirements/observe.in'),
)
