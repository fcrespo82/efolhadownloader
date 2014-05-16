#coding: utf-8
import os
from setuptools import setup

setup(
    name = "efolhadownloader",
    version = "v0.4",
    author = "Fernando Xavier de Freitas Crespo",
    author_email = "fernando82@gmail.com",
    description = ("Faça o download dos \"Demonstrativos de pagamento\" disponibilizados no site http://www.e-folha.sp.gov.br/"),
    long_description = open('README.md').readlines(),
    license = "MIT",
    keywords = "example documentation tutorial",
    url = "https://github.com/fcrespo82/efolhadownloader",
    py_modules = ['efolhadownloader'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires = open('requirements.txt').readlines(),
    entry_points = {
        'console_scripts': ['efolhadownloader = efolhadownloader:main']
    },
)
