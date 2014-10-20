# -*- coding: utf-8 -*-
"""
"""
from setuptools import setup, find_packages

Name = 'pp-utils'
ProjectUrl = ""
Version = "1.0.7"
Author = 'Edward Easton, Oisin Mulvihill'
AuthorEmail = ''
Maintainer = ''
Summary = 'General Utilities.'
License = ''
Description = Summary
ShortDescription = Summary


needed = [
    "python-dateutil",
    "jellyfish",
]

test_needed = [
    "pytest-cov",
]

test_suite = 'pp.utils.tests'

EagerResources = [
    'pp',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

EntryPoints = """
"""

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
        "Topic :: Software Development :: Libraries",
    ],
    keywords='python',
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
