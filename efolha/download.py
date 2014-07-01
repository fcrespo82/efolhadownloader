#!/usr/bin/env python
#coding: utf-8
'''
usage:
    efd.py download ((<a> <m>) | -t | -u) [-d <dir> -p <arquivo> -s <dir> -v -o]

arguments:
    <a>                                Ano de referência
    <m>                                Mês de referência

options:
    -t, --todas                        Listar TODAS as folhas
    -u, --ultima                       Listar a última folha disponível
    -p <arquivo>, --prefixo <arquivo>  Nome do arquivo para ler/salvar as configurações e chave de criptografia [default: efolha]
    -d <dir>, --diretorio <dir>        Diretorio para buscar os arquivos de chave e configurações [default: .]
    -s <dir>, --download_dir <dir>     Diretório para downloads dos arquivos [default: .]
    -o, --sobrescrever                 Sobrescreve o arquivo já existente
    -v, --verbose                      Informa o que o programa está fazendo
'''

import requests
import common

def folha(folha_dict, cookie, options):
    session = requests.session()
    url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'

    local_filename = folha_dict['arquivo']
    #log(u'Fazendo o download da folha {}'.format(folha_dict['Folha']))

    # NOTE the stream=True parameter
    r = session.get(url, stream = True, data = folha_dict, cookies = cookie)
    _dir = options['--download_dir']
    full_path_download = common.full_path(_dir, local_filename)
    #log(u'Caminho completo \'{}\''.format(full_path_download.encode('ascii', 'ignore')))
    if not common.file_exists(folha_dict, options) or options['--sobrescrever']:
        common.log('Fazendo o download do arquivo {}'.format(local_filename))
        with open(full_path_download, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
    else:
        common.log(u'O arquivo {} já existe e não será baixado novamente'.format(local_filename), options)

    return full_path_download