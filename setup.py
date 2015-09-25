#!/usr/bin/env python
# encoding: utf-8

import os

from setuptools import setup, find_packages

setup(
    name="seriesbutler",
    version="1.1.0",
    packages=['seriesbutler'],
    author="Raphael Zimmermann",
    author_email="dev@raphael.li",
    url="https://github.com/raphiz/seriesbutler",
    description="Grab your favourite TV shows",
    long_description=("For more information, please checkout the `Github Page "
                      "<https://github.com/raphiz/seriesbutler>`_."),
    license="MIT",
    platforms=["Linux", "BSD", "MacOS"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'seriesbutler = seriesbutler.cli:cli'
        ]},
    install_requires=open('./requirements.txt').read(),
    tests_require=open('./requirements-dev.txt').read(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        "Programming Language :: Python :: Implementation :: CPython",
        'Development Status :: 4 - Beta',
    ],
)
