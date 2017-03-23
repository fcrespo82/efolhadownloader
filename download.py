#!.venv/bin/python
#coding: utf-8

"""Faz o download dos demonstrativos de pagamento do site e-folha

usage:
    download.py [-d]

options:
    -d          Enable debug messages
"""

import sys
import os
import codecs
from zipfile import ZipFile
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import requests
from docopt import docopt
from secrets import CONFIG
import coloredlogs
sys.dont_write_bytecode = True

PARAMS = docopt(__doc__)

FMT = '%(asctime)s %(levelname)s %(message)s'
DATE_FMT = '%d/%m/%Y %H:%M:%S'
FIELD_STYLES = {'hostname': {'color': 'magenta'}, 'programname': {'color': 'cyan'}, 'name': {'color': 'blue'}, 'levelname': {'color': 'black', 'bold': True}, 'asctime': {'color': 'cyan'}}

LEVEL_STYLES = {'info': {}, 'notice': {'color': 'magenta'}, 'verbose': {'color': 'blue'}, 'spam': {'color': 'green'}, 'critical': {'color': 'red', 'bold': True}, 'error': {'color': 'red'}, 'debug': {'color': 'green'}, 'warning': {'color': 'yellow'}}


if PARAMS['-d']:
    coloredlogs.install(level=logging.DEBUG, fmt=FMT, datefmt=DATE_FMT, level_styles=LEVEL_STYLES, field_Styles=FIELD_STYLES)
    logging.basicConfig(level=logging.DEBUG)
else:
    coloredlogs.install(level=logging.INFO, fmt=FMT, datefmt=DATE_FMT, level_styles=LEVEL_STYLES, field_Styles=FIELD_STYLES)
    logging.basicConfig(level=logging.INFO)

TIPO = {
    1: 'normal',
    3: 'suplementar',
    4: '13º salário'
}

def recupera_nome_e_cliente(session, folha_dict, cookie):
    "Recupera o nome e cliente do e-folha"
    url = 'http://www.e-folha.sp.gov.br/desc_dempagto/DemPagto.asp'
    # NOTE the stream=True parameter
    response = session.get(url, stream=True, data=folha_dict, cookies=cookie)
    soup = BeautifulSoup(response.text, 'lxml')
    cliente = soup.findAll('nobr')[0].text.strip()
    nome = soup.findAll('left')[1].text.strip()
    return nome.replace(' ', '_'), cliente.replace(' ', '_')


SESSION = requests.session()
URL_COOKIE = 'http://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={0}'.format(CONFIG['cliente'].rjust(3, '0'))
URL_LOGIN = 'http://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
URL_LISTA_FOLHAS = 'http://www.e-folha.sp.gov.br/desc_dempagto/Folhas.asp'
URL_DOWNLOAD = 'http://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'

RESPONSE = SESSION.get(URL_COOKIE)
FORM_DATA = {
    'txtMatricula': CONFIG['usuario'].rjust(6, '0'),
    'txtSenha': CONFIG['senha'],
    'txtNPA': '000000000',
    'btOK': 'ENTRAR'
}

COOKIES = RESPONSE.cookies
RESPONSE = SESSION.post(URL_LOGIN, data=FORM_DATA, cookies=COOKIES)

RESPONSE = SESSION.post(URL_LISTA_FOLHAS, cookies=COOKIES)

SOUP = BeautifulSoup(RESPONSE.text, 'lxml')
logging.debug("Buscando tabela que contém arquivos")
TABLE = SOUP.find_all('table', attrs={'class':'tabela'})
logging.debug("Buscando links para PDF")
PDFS = TABLE[0].find_all('img', attrs={'alt':'pdf'})
FOLHAS = []
NOME = ''
CLIENTE = ''

for pdf in PDFS:
    logging.debug("PDF: " + str(pdf))
    valores = pdf['onclick'][10:-3].split('\',\'')

    _tipo = int(valores[0])
    _sequencia = valores[1].rjust(2, '0')
    _mesref = valores[2].rjust(2, '0')
    _anoref = valores[3]

    detalhes = {
        'Folha': 'Folha ref {0}/{1} tipo {2}'.format(
            _mesref, _anoref, TIPO[int(_tipo)]),
        'Tipo': _tipo,
        'sequencia': _sequencia,
        'mesref': _mesref,
        'anoref': _anoref
    }

    if NOME == '' or CLIENTE == '':
        logging.info('Buscando nomes')
        NOME, CLIENTE = recupera_nome_e_cliente(SESSION, detalhes, COOKIES)

    detalhes.update({
        'arquivo': '{0}_{1}-Pagamentox-{3}-{4}_{5}_{2}.pdf'.format(
            _anoref, _mesref, TIPO[int(_tipo)], NOME, CLIENTE, _sequencia),
        'nome': NOME,
        'cliente': CLIENTE,
        'description': '{0}_{1}-{2}-{3}_{4}_{2}.pdf'.format(
            _anoref, _mesref, TIPO[int(_tipo)],
            NOME.split('_')[0], CLIENTE.split('_')[-1])
    })

    FOLHAS.append(detalhes)

CONFIG['output_dir'] = os.path.realpath(os.path.expanduser(
    CONFIG['output_dir']))

DATE = datetime.strftime(datetime.now(), '%Y_%m_%d-%H_%M_%S')

FULL_PATH_ZIP = os.path.join(CONFIG['output_dir'], 'folhas-' + DATE + '.zip')
FULL_PATH_LOG = os.path.join(CONFIG['output_dir'], 'folhas.log')

ALREADY_DOWNLOADED = []
if os.path.exists(FULL_PATH_LOG):
    with codecs.open(FULL_PATH_LOG, 'r', 'utf-8') as mylog:
        ALREADY_DOWNLOADED = mylog.readlines()

ALREADY_DOWNLOADED = [_file.replace('\n', '') for _file in ALREADY_DOWNLOADED]

DOWNLOADED = []
for folha in FOLHAS:
    full_path_download = os.path.join(CONFIG['output_dir'], folha['arquivo'])

    if not os.path.exists(CONFIG['output_dir']):
        os.makedirs(CONFIG['output_dir'])

    if folha['arquivo'] not in ALREADY_DOWNLOADED:
        DOWNLOADED.append(folha['arquivo'])
        r = SESSION.post(URL_DOWNLOAD, stream=True, data=folha, cookies=COOKIES)
        msg = 'Baixando: {0}'.format(folha['description'])
        logging.info(msg)
        with open(full_path_download, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
    else:
        msg = 'JÁ EXISTE: {0}'.format(folha['description'])
        logging.warning(msg)

if len(DOWNLOADED) > 0:
    with codecs.open(FULL_PATH_LOG, 'a+', 'utf-8') as mylog:
        for _file in DOWNLOADED:
            if _file not in ALREADY_DOWNLOADED:
                mylog.write(_file + '\n')

    if CONFIG['send_mail']:
        logging.info('Comprimindo arquivos baixados')
        with ZipFile(FULL_PATH_ZIP, 'w') as myzip:
            for _file in DOWNLOADED:
                full_path_file = os.path.join(CONFIG['output_dir'], _file)
                myzip.write(full_path_file, _file)

        from send_mail import SendMail

        MAIL = SendMail()

        MAIL.send(FULL_PATH_ZIP)
