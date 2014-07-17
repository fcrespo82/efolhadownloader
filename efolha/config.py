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
    common.log(u'Gerando hash', arguments)
    import md5
    _hash = md5.new(arguments['<cliente>'])
    _hash.update(arguments['<usuario>'])
    _hash.update(arguments['<senha>'])
    key = _hash.hexdigest()
    return key

def _load_config(arguments):
    common.log(u'Carregando arquivo de configuração', arguments)
    return common.load_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.config'), arguments)

def _load_key(arguments):
    common.log(u'Carregando arquivo de chave', arguments)
    return common.load_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.key'), arguments)

def _save_key(arguments):
    common.log(u'Preparando chave', arguments)
    _key = _generate_hash(arguments)
    common.save_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.key'), _key, arguments)
    return _key

def _save_config(arguments):
    common.log(u'Preparando configuração', arguments)
    _key = _load_key(arguments)
    _config = common.build_dict(arguments)
    _encrypted = common.encrypt(_key, json.dumps(_config), arguments)
    common.save_file(common.full_path(arguments['--diretorio'], arguments['--prefixo'] + '.config'), _encrypted, arguments)

def load(arguments):
    common.log(u'Carregando configuração', arguments)
    _key = _load_key(arguments)
    _config = _load_config(arguments)
    _data = common.decrypt(_key, _config, arguments)
    common.log(u'Configuração carregada', arguments)
    return json.loads(_data)

def save(arguments):
    common.log(u'Salvando configuração', arguments)
    _save_key(arguments)
    _save_config(arguments)
    common.log(u'Configuração salva', arguments)

