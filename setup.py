#! /usr/bin/env python

from setuptools import setup

import setuptools


setup(
    name='drawstools',
    # Please read the following for setting the version number:
    #    - https://pythonhosted.org/setuptools/setuptools.html#specifying-your-project-s-version  # noqa
    version='0.0.0',
    author='Pedro H <pedro@digitalrounin.com>',
    author_email='pedro@digitalrounin.com',
    packages=setuptools.find_packages(),
    install_requires=[
        'awscli>=1.10.38',
        'boto3>=1.3.1',
        'colorama==0.3.3',
        'PyYAML>=3.11'
    ],
    entry_points={'console_scripts': [
        'draws-instance-statuses = drawstools.instance:list_status',
    ]},
    # include_package_data=True,
    # package_data={
    #     'conf': ['conf/*'],
    # }
    )
