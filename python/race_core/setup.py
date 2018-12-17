#!/usr/bin/env python

from distutils.core import setup

setup(
    name='OpenRace',
    version='0.1',
    description='OpenRace',
    author='Marc Urben',
    author_email='aegnor@mittelerde.ch',
    url='https://github.com/oxivanisher/OpenRace',
    packages=['race_core'],
    entry_points = {
        'console_scripts': [
            'race_core = race_core.core:main',
        ]
    }
)
