#!/usr/bin/env python

from distutils.core import setup

setup(
    name='OpenRace',
    version='0.1',
    description='OpenRace',
    author='Marc Urben',
    author_email='aegnor@mittelerde.ch',
    url='',
    packages=['race_core'],
    entry_points = {
        'console_scripts': [
            'openrace = race_core.core:main',
        ]
    }
)
