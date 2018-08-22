#!/usr/bin/env python
# -*- coding: UTF-8 -*-import os
from setuptools import setup
import os
version_file = open(os.path.join('.', 'version.txt'))

setup(
    name = 'videoai-sdk',
    version=version_file.read().strip(),
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
        'oauth2client>=4.1.2'
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Topic :: Video Processing :: Analytics',
        ],
)
