#!/usr/bin/python
#coding: utf-8
'''
usage:
    efolhadownloader.py listar ((<a> <m>) | -t | -u) [-d <dir> -p <arquivo> -s <dir> -v]

arguments:
    <a>                                Ano de referência
    <m>                                Mês de referência

options:
    -t, --todas                        Listar TODAS as folhas
    -u, --ultima                       Listar a última folha disponível
    -p <arquivo>, --prefixo <arquivo>  Nome do arquivo para ler/salvar as configurações e chave de criptografia [default: efolha]
    -d <dir>, --diretorio <dir>        Diretorio para buscar os arquivos de chave e configurações [default: .]
    -s <dir>, --download_dir <dir>     Diretório para downloads dos arquivos [default: .]
    -v, --verbose                      Informa o que o programa está fazendo
'''