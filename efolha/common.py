#!/usr/bin/env python
#coding: utf-8

from subprocess import Popen, PIPE
import os
import shlex
import datetime

def encrypt(password, text, arguments):
    log(u'Criptografando texto', arguments)
    _command=shlex.split(u'openssl enc -aes-256-cbc -e -a -pass')
    _command.append(u'pass:' + password)
    po = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = po.communicate(text)
    return stdout #{u'stdout': stdout, u'error': stderr, u'return_code': po.returncode }

def decrypt(password, text, arguments):
    log(u'Descriptografando texto', arguments)
    _command=shlex.split(u'openssl enc -aes-256-cbc -d -a -pass')
    _command.append(u'pass:' + password)
    po = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = po.communicate(text)
    return stdout #{u'stdout': stdout, u'error': stderr, u'return_code': po.returncode }

def log(message, arguments=None, force=False):
    if (arguments != None and arguments.has_key('--verbose') and arguments['--verbose']) or force:
        _datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(_datetime + ' - ' + message)

def build_dict(arguments):
    log(u'Criando objeto', arguments)
    return {
        'cliente': arguments['<cliente>'],
        'usuario': arguments['<usuario>'],
        'senha': arguments['<senha>']
    }

def dir_exists(path):
    return os.path.exists(path)

def file_exists(folha_dict, arguments):
    _dir = arguments['--download_dir']
    _full_path = full_path(_dir, folha_dict['arquivo'])
    return os.path.exists(_full_path)

def full_path(path, filename=''):
    return os.path.realpath(os.path.expanduser(os.path.join(path, filename)))

def rec(x):
    if x > 0:
        rec(x-1)

    print x

def make_dirs(path, arguments):
    fullpath = full_path(path)
    parent = '/'.join(fullpath.split('/')[:-1])
    _dir = ''.join(fullpath.split('/')[-1])

    if not dir_exists(parent):
        make_dirs(parent)

    if not dir_exists(fullpath):
        log(u'Criando diretório {}'.format(fullpath), arguments)
        os.mkdir(fullpath)

def load_file(path, arguments):
    log(u'Carregando arquivo {}'.format(path), arguments)
    _contents = ""
    try:
        with open(path, 'rb') as _file:
            _contents = _file.readlines()
        return "".join(_contents)
    except IOError, e:
        log(u'The file {} do not exists.'.format(path), force=True)
        exit(0)


def save_file(path, text, arguments):
    log(u'Salvando arquivo {}'.format(path), arguments)
    with open(path, 'wb') as _file:
        _file.write(text)
