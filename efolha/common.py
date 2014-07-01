#!/usr/bin/env python
#coding: utf-8

from subprocess import Popen, PIPE
import os
import shlex
import datetime

def encrypt(password, text):
    _command=shlex.split(u'openssl enc -aes-256-cbc -e -a -pass')
    _command.append(u'pass:' + password)
    po = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = po.communicate(text)
    return stdout #{u'stdout': stdout, u'error': stderr, u'return_code': po.returncode }

def decrypt(password, text):
    _command=shlex.split(u'openssl enc -aes-256-cbc -d -a -pass')
    _command.append(u'pass:' + password)
    po = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = po.communicate(text)
    return stdout #{u'stdout': stdout, u'error': stderr, u'return_code': po.returncode }

def log(message, options, force=False):
    if options.has_key('--verbose') or force:
        _datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(_datetime + ' - ' + message)

def build_dict(arguments):
    return {
        'cliente': arguments['<cliente>'],
        'usuario': arguments['<usuario>'],
        'senha': arguments['<senha>']
    }

def file_exists(folha_dict, options):
    _dir = options['--download_dir']
    _full_path = full_path(_dir, folha_dict['arquivo'])
    return os.path.exists(_full_path)

def full_path(path, filename):
    return os.path.realpath(os.path.expanduser(os.path.join(path, filename)))

def load_file(path):
    _contents = ""
    with open(path, 'rb') as _file:
        _contents = _file.readlines()
    return "".join(_contents)

def save_file(path, text):
    with open(path, 'wb') as _file:
        _file.write(text)
