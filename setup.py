import os
from setuptools import find_packages, setup

name = 'pyfluent'
version = '0.1.0'
readme = os.path.join(os.path.dirname(__file__), 'README.rst')
long_description = open(readme).read()

classifiers = [
    'Development Status :: 1 - Planning',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'Programming Language :: Python',
    'License :: OSI Approved :: MIT License',
    'Topic :: System :: Logging',
    'Topic :: System :: Networking'
]

setup(name=name,
      version=version,
      description='A python client library for Fluentd',
      long_description=long_description,
      classifiers=classifiers,
      keywords=['logging', 'fluentd', 'json'],
      author='Yoshihisa Tanaka',
      author_email='yt.hisa@gmail.com',
      license='MIT',
      install_requires=['msgpack-python>=0.1.12'],
      packages=find_packages(exclude=['*.tests*'])
)
