import os
from setuptools import find_packages, setup

name = 'pyfluent'
version = '0.1.1'
readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

classifiers = [
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
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
