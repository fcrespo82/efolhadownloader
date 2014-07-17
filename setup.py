#!/usr/bin/env python
#coding: utf-8
import os
from setuptools import setup
import efd

setup(
    name = "efolhadownloader",
    version = efd.__version__,
    author = "Fernando Xavier de Freitas Crespo",
    author_email = "fernando82@gmail.com",
    description = ("Faça o download dos \"Demonstrativos de pagamento\" disponibilizados no site http://www.e-folha.sp.gov.br/"),
    long_description = unicode('\n'.join(open('README.md').readlines()).decode('utf-8')),
    license = u'\n'.join(open('LICENSE').readlines()),
    keywords = "efolha download automation",
    url = "https://github.com/fcrespo82/efolhadownloader",
    py_modules = ['efd'],
    packages = ['efolha'],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires = open('requirements.txt').readlines(),
    entry_points = {
        'console_scripts': ['efd = efd:main', 'efolha = efd:main']
    },
)
