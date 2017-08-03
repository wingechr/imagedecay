#!/usr/bin/env python3
# coding: utf-8

import codecs
from setuptools import setup, find_packages
import unittest
import conf


def read(f):
    return codecs.open(f, 'rb', 'utf8').read()


def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests')
    return test_suite


if __name__ == "__main__":
    setup(
        name=conf.package,
        version=conf.version,
        description=conf.description,
        long_description=read('README.md'),
        url=conf.url,
        author=conf.author,
        author_email=conf.author_email,
        license=conf.license,
        packages=find_packages('src'),
        zip_safe=False,
        classifiers=[  # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5'
        ],
        platforms='any',
        # Packages and dependencies
        package_dir={'': 'src'},
        install_requires=read('requirements.txt').splitlines(),
        include_package_data=True,  # include files from MANIFEST.in,
        test_suite='setup.run_tests',  # do tests
    )
