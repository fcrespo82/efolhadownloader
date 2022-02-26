#!/usr/bin/env python
import logging
import os
import gettext
import argparse
import sys
import requests
from bs4 import BeautifulSoup

VERSION = '1.0.0'


def setup_argparse():
    locale_dir = os.path.join(os.path.dirname(__file__), "locale")
    argparse_ptbr_translation = gettext.translation(
        'argparse', localedir=locale_dir, languages=['pt_BR'])

    # Substitui métodos nativos do argparse com tradução em pt_BR
    # pyright: reportGeneralTypeIssues=none
    argparse.gettext = argparse_ptbr_translation.gettext
    argparse.ngettext = argparse_ptbr_translation.ngettext
    argparse._ = argparse.gettext

    parser = argparse.ArgumentParser(
        description=f'Download PDFs do e-folha - v{VERSION}')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Mostra mensagens de debug')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Aumenta a verbosidade')
    parser.add_argument('cliente', type=int,
                        choices=[50, 21], help='ID do cliente no e-folha (50=ALESP ou 21=TJ)')
    parser.add_argument('matricula', type=int, help='Matrícula do funcionário')
    parser.add_argument('senha', type=str, help='Senha do funcionário')
    parser.add_argument('-o', dest='output', type=str, default='./saida',
                        help='Caminho para salvar os arquivos (Padrão: ./saida) ')
    return parser


def main():
    if (sys.argv[0].endswith('main.py')):
        logging.critical(
            'Please run this script from \'efolha-cli\' from root folder')
        exit(1)
    parser = setup_argparse()
    args = parser.parse_args()
    log = logging.getLogger()
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if args.debug:
        log.setLevel(logging.DEBUG)
        log.debug(args)
    elif args.verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    session, response = get_html_folhas(args, log)

    all_links = extrai_links(log, response)

    download_arquivos(args, log, session, all_links)


def download_arquivos(args, log, session, all_links):
    log.info('Salvando arquivos em: ' + args.output)
    for link in all_links:
        tipo, sequencia, mesref, anoref, str_target = link['onclick'].replace(
            'Atualiza(', '').replace(');', '').replace('\'', '').split(',')

        local_filename = os.path.realpath(f'{args.output}/{args.matricula}/{anoref}/'
                                          f'{anoref}-{mesref}-{tipo}-{sequencia}-{args.matricula}.pdf')
        log.debug(local_filename)
        if not os.path.exists(os.path.dirname(local_filename)):
            os.makedirs(os.path.dirname(local_filename), exist_ok=True)

        if not os.path.exists(local_filename):
            log.info('Baixando folha %s-%s-%s', anoref, mesref, sequencia)
            response = session.post(
                'https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/DemPagtoP.asp',
                data={
                    'Tipo': tipo,
                    'sequencia': sequencia,
                    'mesref': mesref,
                    'anoref': anoref,
                    'strTarget': str_target
                }, stream=True)
            with open(local_filename, 'wb') as output_pdf:
                for chunk in response.iter_content(chunk_size=8192):
                    output_pdf.write(chunk)
        else:
            log.warning('Arquivo %s já existe', local_filename)


def extrai_links(log, response):
    soup = BeautifulSoup(response.text, 'html5lib')
    all_links = soup.find_all('img', {'alt': 'pdf', 'onclick': True})
    log.debug(all_links)
    return all_links


def get_html_folhas(args, log):
    session = requests.Session()
    log.debug('Pegando cookie')
    response = session.get(f'https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/entrada.asp?'
                           f'cliente={str(args.cliente).zfill(3)}')
    log.debug(response.cookies)

    log.debug('Fazendo login')
    response = session.post('https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/PesqSenha.asp',
                            data={
                                'txtMatricula': str(args.matricula).zfill(6),
                                'txtSenha': args.senha,
                                'txtNPA': '000000000',
                                'btOK': 'ENTRAR'
                            })
    log.debug(response.status_code)

    log.debug('Listando folhas')
    response = session.post(
        'https://www.e-folha.prodesp.sp.gov.br/desc_dempagto/Folhas.asp')

    return session, response


if __name__ == '__main__':
    main()
