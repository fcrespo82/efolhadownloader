#!/usr/bin/env python
#coding: utf-8
'''
usage:
    efd.py config <cliente> <usuario> <senha> [-d <dir> -p <arquivo> -v]

arguments:
    <cliente>                          Cliente
    <usuario>                          Matrícula
    <senha>                            Senha

options:
    -d <dir>, --diretorio <dir>        Diretório para salvar os arquivos de chave e configurações [default: .]
    -p <prefixo>, --prefixo <prefixo>  Prefixo dos nomes de arquivo para salvar as configurações e chave de criptografia [default: efolha]
    -v, --verbose                      Informa o que o programa está fazendo
'''

from efolha import common
import json

def _generate_hash(arguments):
    import md5
    _hash = md5.new(arguments['<cliente>'])
    _hash.update(arguments['<usuario>'])
    _hash.update(arguments['<senha>'])
    key = _hash.hexdigest()
    return key

def _load_config(arguments):
    return common.load_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.config'))

def _load_key(arguments):
    return common.load_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.key'))

def _save_key(arguments):
    _key = _generate_hash(arguments)
    common.save_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.key'), _key)
    return _key

def _save_config(arguments):
    _key = _load_key(arguments)
    _config = common.build_dict(arguments)
    _encrypted = common.encrypt(_key, json.dumps(_config))
    common.save_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.config'), _encrypted)

def load(arguments):
    _key = _load_key(arguments)
    _config = _load_config(arguments)
    _data = common.decrypt(_key, _config)
    return json.loads(_data)

def save(arguments):
    _save_key(arguments)
    _save_config(arguments)

