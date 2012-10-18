# -*- coding: utf-8 -*-
"""
Setuptools script for pp-utils (pp.utils)

"""

from setuptools import setup, find_packages

Name = 'pp-utils'
ProjectUrl = ""
Version = "1.0.1dev"
Author = ''
AuthorEmail = 'everyone at pythonpro dot co dot uk'
Maintainer = ''
Summary = ' pp-utils '
License = ''
Description = Summary
ShortDescription = Summary

needed = [
    'sphinx', # for docs generation.
    'evasion-common',
]

test_needed = [
]

test_suite = 'pp.utils.tests'

EagerResources = [
    'pp',
]

# Example including shell script out of scripts dir
ProjectScripts = [
#    'pp.utils/scripts/somescript',
]

PackageData = {
    '': ['*.*'],
}

# Example console script and paster template integration:
EntryPoints = {
}


setup(
    url=ProjectUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    classifiers=[
      "Programming Language :: Python",
      "Framework :: Pylons",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    tests_require=test_needed,
    test_suite=test_suite,
    include_package_data=True,
    packages=find_packages(),
    package_data=PackageData,
    eager_resources=EagerResources,
    entry_points=EntryPoints,
    namespace_packages=['pp'],
)
