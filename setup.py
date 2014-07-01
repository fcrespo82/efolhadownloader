#coding: utf-8
import os
from setuptools import setup

setup(
    name = "efolhadownloader",
    version = "0.5",
    author = "Fernando Xavier de Freitas Crespo",
    author_email = "fernando82@gmail.com",
    description = ("Faça o download dos \"Demonstrativos de pagamento\" disponibilizados no site http://www.e-folha.sp.gov.br/"),
    long_description = u'\n'.join(open('README.md').readlines()),
    license = "MIT",
    keywords = "example documentation tutorial",
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
        'console_scripts': ['efolhadownloader = efolhadownloader:main']
    },
)
