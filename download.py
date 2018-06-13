#!.venv/bin/python
#coding: utf-8

'Faz o download dos demonstrativos de pagamento do site e-folha'

import os
import codecs
import logging
import argparse
from secrets import CONFIG
from bs4 import BeautifulSoup
import requests
import coloredlogs

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-v', '--verbose', help='Be verbose', action='store_true')

ARGS = PARSER.parse_args()


FMT = '%(asctime)s %(levelname)s %(message)s'
DATE_FMT = '%d/%m/%Y %H:%M:%S'
FIELD_STYLES = {'hostname': {'color': 'magenta'}, 'programname': {'color': 'cyan'}, 'name': {
    'color': 'blue'}, 'levelname': {'color': 'black', 'bold': True}, 'asctime': {'color': 'cyan'}}

LEVEL_STYLES = {'info': {}, 'notice': {'color': 'magenta'}, 'verbose': {'color': 'blue'}, 'spam': {'color': 'green'}, 'critical': {
    'color': 'red', 'bold': True}, 'error': {'color': 'red'}, 'debug': {'color': 'green'}, 'warning': {'color': 'yellow'}}


if ARGS.verbose:
    coloredlogs.install(level=logging.DEBUG, fmt=FMT, datefmt=DATE_FMT,
                        level_styles=LEVEL_STYLES, field_Styles=FIELD_STYLES)
    logging.basicConfig(level=logging.DEBUG)
else:
    coloredlogs.install(level=logging.INFO, fmt=FMT, datefmt=DATE_FMT,
                        level_styles=LEVEL_STYLES, field_Styles=FIELD_STYLES)
    logging.basicConfig(level=logging.INFO)

TIPO = {
    1: 'normal',
    3: 'suplementar',
    4: '13º salário'
}


def recupera_nome_e_cliente(session, folha_dict, cookie):
    'Recupera o nome e cliente do e-folha'
    url = 'http://www.e-folha.sp.gov.br/desc_dempagto/DemPagto.asp'
    # NOTE the stream=True parameter
    response = session.get(url, stream=True, data=folha_dict, cookies=cookie)
    soup = BeautifulSoup(response.text, 'lxml')
    cliente = soup.findAll('nobr')[0].text.strip()
    nome = soup.findAll('left')[1].text.strip()
    return nome.replace(' ', '_'), cliente.replace(' ', '_')


def download():
    'Faz o download das folhas'
    session = requests.session()
    url_cookie = 'http://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={0}'.format(
        CONFIG['cliente'].rjust(3, '0'))
    url_login = 'http://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
    url_lista_folhas = 'http://www.e-folha.sp.gov.br/desc_dempagto/Folhas.asp'
    url_download = 'http://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'

    response = session.get(url_cookie)
    form_data = {
        'txtMatricula': CONFIG['usuario'].rjust(6, '0'),
        'txtSenha': CONFIG['senha'],
        'txtNPA': '000000000',
        'btOK': 'ENTRAR'
    }

    response = session.post(url_login, data=form_data,
                            cookies=response.cookies)
    response = session.post(url_lista_folhas, cookies=response.cookies)
    soup = BeautifulSoup(response.text, 'lxml')
    logging.debug('Buscando tabela que contém arquivos')
    table = soup.find_all('table', attrs={'class': 'tabela'})
    logging.debug('Buscando links para PDF')
    pdfs = table[0].find_all('img', attrs={'alt': 'pdf'})
    folhas = []
    nome = None
    cliente = None
    for pdf in pdfs:
        logging.debug('PDF: %s', str(pdf))
        valores = pdf['onclick'][10:-3].split('\',\'')

        _tipo, _sequencia, _mesref, _anoref, _ = valores

        detalhes = {
            'Folha': 'Folha ref {0}/{1} tipo {2}'.format(
                _mesref, _anoref, TIPO[int(_tipo)]),
            'Tipo': _tipo,
            'tipo_str': TIPO[int(_tipo)],
            'sequencia': _sequencia,
            'mesref': _mesref,
            'anoref': _anoref
        }

        if not nome or not cliente:
            logging.info('Buscando nomes')
            nome, cliente = recupera_nome_e_cliente(
                session, detalhes, response.cookies)
            logging.info('nome=%s, cliente=%s', nome, cliente)

        detalhes.update({'nome': nome, 'cliente': cliente})

        detalhes.update({
            'arquivo': '{anoref}_{mesref}-Pagamentox-{nome}-{cliente}_{sequencia}_{tipo_str}.pdf'.format(**detalhes),
            'description': '{anoref}_{mesref}-{nome}_{cliente}_{tipo_str}.pdf'.format(**detalhes)
        })

        logging.debug(detalhes)
        folhas.append(detalhes)

    CONFIG['output_dir'] = os.path.realpath(os.path.expanduser(
        CONFIG['output_dir']))

    full_path_log = os.path.join(CONFIG['output_dir'], 'folhas.log')
    already_downloaded = []
    if os.path.exists(full_path_log):
        with codecs.open(full_path_log, 'r', 'utf-8') as mylog:
            already_downloaded = mylog.readlines()

    already_downloaded = [_file.replace('\n', '')
                          for _file in already_downloaded]

    downloaded = []
    for folha in folhas:
        full_path_download = os.path.join(
            CONFIG['output_dir'], folha['arquivo'])

        if not os.path.exists(CONFIG['output_dir']):
            os.makedirs(CONFIG['output_dir'])

        if folha['arquivo'] not in already_downloaded:
            downloaded.append(folha['arquivo'])
            response = session.post(url_download, stream=True,
                                    data=folha, cookies=response.cookies)
            msg = 'Baixando: {0}'.format(folha['description'])
            logging.info(msg)
            with open(full_path_download, 'wb') as _file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        _file.write(chunk)
                        _file.flush()
        else:
            msg = 'JÁ EXISTE: {0}'.format(folha['description'])
            logging.warning(msg)

    logging.info(CONFIG['output_dir'])

    if downloaded:
        with codecs.open(full_path_log, 'a+', 'utf-8') as mylog:
            for _not_downloaded in (_file for _file in downloaded if _file not in already_downloaded):
                mylog.write(_not_downloaded + '\n')


if __name__ == '__main__':
    download()
