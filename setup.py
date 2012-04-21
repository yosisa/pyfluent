# -*- coding: utf-8 -*-
# Copyright 2012 Yoshihisa Tanaka
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from setuptools import find_packages, setup

name = 'pyfluent'
version = '0.2.0'
readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: System :: Logging',
    'Topic :: System :: Networking'
]

setup(name=name,
      version=version,
      author='Yoshihisa Tanaka',
      author_email='yt.hisa@gmail.com',
      license='MIT',
      url='https://github.com/yosisa/pyfluent',
      description='A python client library for Fluentd',
      long_description=long_description,
      classifiers=classifiers,
      keywords=['logging', 'fluentd', 'json'],
      install_requires=['msgpack-python>=0.1.12'],
      tests_require=['pytest', 'mock'],
      packages=find_packages(exclude=['tests'])
)
