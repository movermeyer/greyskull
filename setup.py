#!/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from greyskull import (__version__ as version,
                       __license__ as license,
                       __author__ as author,
                       __email__ as author_email)

setup(
    name="Greyskull",
    version=version,
    description="A lightweight bittorrent tracker",
    long_description=open("README.txt", 'rb').read().decode('utf-8'),
    license=license,
    author=author,
    author_email=author_email,
    packages=[
        'greyskull',
    ],
    install_requires=[
        'tornado',
    ],
    classifiers=[]
)
