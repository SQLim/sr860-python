from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='sr860-python',
    version='0.1.0',
    author='Shao Qi Lim',
    author_email='qiqilsq@gmail.com',
    description='Python package for Windfreak Technologies devices.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SQLim/sr860-python',
    packages=find_packages(exclude=['examples']),
    install_requires=[
        'pyvisa',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    python_requires='>=3',
)
