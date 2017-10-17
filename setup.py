#!/usr/bin/env python
# -*- coding: UTF-8 -*-import os
from setuptools import setup

setup(
    name = 'videoai-sdk',
    version='5.1',
    description='An SDK for accessing VideoAI',
    keywords='video processing, machine learning, security, analytics, face-recognition',
    license='Commercial',
    author='Kieron Messer',
    author_email='kieron.messer@digitalbarriers.com',
    packages =['videoai',
              'videoai.recognition',
              ],
    scripts =[],
    platforms='any',
    install_requires=[
        'requests>=2.11',
        'configparser>=3.5',
        'oauth2>=1.9',
        'oauth2client>=1.2'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Topic :: Video Processing :: Analytics',
        ],
)
