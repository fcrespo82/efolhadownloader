#!/usr/bin/python
#coding: utf-8
'''
usage:
    efolhadownloader.py config <cliente> <usuario> <senha> [-d <dir> -p <arquivo> -v]

arguments:
    <cliente>                          Cliente
    <usuario>                          Matrícula
    <senha>                            Senha

options:
    -d <dir>, --diretorio <dir>        Diretório para buscar os arquivos de chave e configurações [default: .]
    -p <prefixo>, --prefixo <prefixo>  Prefixo dos nomes de arquivo para ler/salvar as configurações e chave de criptografia [default: efolha]
    -v, --verbose                      Informa o que o programa está fazendo
'''

import efd_common
import json

def _generate_hash(arguments):
    import md5
    _hash = md5.new(arguments['<cliente>'])
    _hash.update(arguments['<usuario>'])
    _hash.update(arguments['<senha>'])
    key = _hash.hexdigest()
    return key

def _load_config(arguments):
    return efd_common.load_file(efd_common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.config'))

def _load_key(arguments):
    return efd_common.load_file(efd_common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.key'))

def _save_key(arguments):
    _key = _generate_hash(arguments)
    efd_common.save_file(efd_common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.key'), _key)
    return _key

def _save_config(arguments):
    _key = _load_key(arguments)
    _config = efd_common.build_dict(arguments)
    _encrypted = efd_common.encrypt(_key, json.dumps(_config))
    efd_common.save_file(efd_common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.config'), _encrypted)

def return_config(arguments):
    _key = _load_key(arguments)
    _config = _load_config(arguments)
    _data = efd_common.decrypt(_key, _config)
    return json.loads(_data)

def save_config(arguments):
    _save_key(arguments)
    _save_config(arguments)