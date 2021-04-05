#!/usr/bin/env python

from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="bots",
    version="0.1",
    description="Collection of bots",
    author="Benjamin Bolte",
    url="https://github.com/codekansas/bots",
    license="MIT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["bots"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "torch",
        "termcolor",
        "coloredlogs",
        "lxml",
        "croniter",
    ],
    python_requires=">=3.7",
    extras_require={
        "testing": [
            "pytest",
        ],
    },
    include_package_data=True,
)
