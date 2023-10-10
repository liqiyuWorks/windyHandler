#!python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
import windyHandler

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="windyHandler",
    version=windyHandler.__version__,
    author="liqiyu",
    author_email="liqiyuworks@163.com",
    description="A python library that can access and process the data from www.windy.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/liqiyuWorks/windyHandler",
    py_modules=['windyHandler'],
    install_requires=["requests >= 2.29.0"],
    classifiers=[
        "Topic :: Games/Entertainment ",
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Games/Entertainment :: Board Games',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
