#!/usr/bin/env bash

python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

if [ ! -e "$(which git-crypt)" ]
then
    echo "Please install git-crypt"
    pacaur -S git-crypt
else
    echo "git-crypt already installed"
fi