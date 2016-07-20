#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Eve',
    'flask-neo4j',
    'py2neo'
]

test_requirements = [
    'pytest'
]

setup(
    name='eve_neo4j',
    version='0.1.1',
    description="Eve Neo4j extension.",
    long_description=readme + '\n\n' + history,
    author="Rodrigo Rodriguez",
    author_email='rrodriguez@grupoabraxas.com',
    url='https://github.com/Abraxas-Biosystems/eve-neo4j',
    packages=[
        'eve_neo4j',
    ],
    dependency_links = [
        'http://github.com/rodrigorn/flask-neo4j/tarball/master#egg=flask-neo4j'
    ],
    package_dir={'eve_neo4j':
                 'eve_neo4j'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='eve_neo4j',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='eve_neo4j.tests',
    tests_require=test_requirements
)
