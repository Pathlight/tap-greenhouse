#!/usr/bin/env python
from setuptools import setup

setup(
    name="tap-greenhouse",
    version="0.2.0",
    description="Singer.io tap for extracting data",
    author="Stitch",
    url="http://singer.io",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["tap_greenhouse"],
    install_requires=[
        # NB: Pin these to a more specific version for tap reliability
        "singer-python",
        "requests",
    ],
    entry_points="""
    [console_scripts]
    tap-greenhouse=tap_greenhouse:main
    """,
    packages=["tap_greenhouse"],
    package_data = {
        "schemas": ["tap_greenhouse/schemas/*.json"]
    },
    include_package_data=True,
)
