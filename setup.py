from setuptools import find_packages, setup

VERSION = "1.0.0"

setup(
    name="rscraping",
    version=VERSION,
    author="Iago Santos",
    packages=find_packages(),
    install_requires=[
        "parsel",
        "pypdf",
        "requests",
        "simplemma",
    ],
    dependency_links=["https://github.com/iagocanalejas/pyutils.git@master#egg=pyutils"],
)
