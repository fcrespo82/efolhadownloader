#!/usr/bin/env python
#coding: utf-8

from docopt import docopt
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import datetime
import json
from Crypto.Cipher import AES
import md5

__version__ = '0.3'

__doc__ = '''usage:   
    efolhadownloader.py download [--config <arquivo>] ((-a <a> -m <m>) | --todas | --ultima) [--listar] [--verbose]
    efolhadownloader.py cria_config <cliente> <usuario> <senha> [--config <arquivo>] [--chave <arquivo>] [--verbose]
    efolhadownloader.py --version

cria_config options:
    <cliente>               Cliente
    <usuario>               Matrícula
    <senha>                 Senha

download options:
    -a <a>                  Ano de referência
    -m <m>                  Mês de referência
    --todas                 Fazer o download de TODAS as folhas
    --ultima                Fazer o download da última folha disponível
    --listar                Apenas lista as folhas (NÃO faz download)

common options:
    --config <arquivo>      Nome do arquivo para ler/salvar as configurações [default: efolha.config]
    --chave <arquivo>       Nome do arquivo para salvar a chave de criptografia [default: efolha.key]
    --verbose               Informa o que o programa está fazendo
'''
options = docopt(__doc__, version=__version__)

def main():
    def encrypt(key, message):
        def _roundUp(numToRound, multiple):
            return (numToRound + multiple - 1) // multiple * multiple;
        def _paddedString(string):
            return string.ljust(_roundUp(len(string),8), '\x00')
        padded_message = _paddedString(message)
        return AES.new(key).encrypt(padded_message)

    def decrypt(key, message):
        decrypted = AES.new(key).decrypt(message)
        return decrypted.replace('\x00','')

    def log(message, force=False):
        if options['--verbose'] or force:
            _datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pprint(_datetime + ' - ' + message)

    log('Iniciando')
    if options['cria_config']:
        log('Criando hash dos dados de entrada')
        _hash = md5.new(options['<cliente>'])
        _hash.update(options['<usuario>'])
        _hash.update(options['<senha>'])
        key = _hash.hexdigest()
        log('Hash: {}'.format(key))
        log('Salvando hash no arquivo {}'.format(options['--chave']))
        with open(options['--chave'], 'wb') as key_file:
            key_file.write(key)

        config = {
            'cliente': options['<cliente>'],
            'usuario': options['<usuario>'],
            'senha': options['<senha>']
        }

        log('Encriptando dados de entrada')
        encrypted = encrypt(key, json.dumps(config))

        log('Salvando dados encriptados no arquivo {}'.format(options['--config']))
        with open(options['--config'], 'wb') as config_file:
            config_file.write(encrypted)
        log('Finalizado\n')
        exit(0)
    elif options['download']:
        log('Carregando dados do arquivo {}'.format(options['--config']))
        with open(options['--config'], 'rb') as config_file:
            file_data=config_file.readlines()
            encrypted = ''.join(file_data)
        log('Desencriptando dados com a chave contida no arquivo'.format(options['--chave']))
        with open(options['--chave'],'rb') as key_file:
            key = ''.join(key_file.readlines())
        decrypted = decrypt(key, encrypted)
        config = json.loads(decrypted)

        options['<cliente>'] = config['cliente']
        options['<usuario>'] = config['usuario']
        options['<senha>'] = config['senha']
        log('Dados carregados')

    enum_tipo = {
        1: 'normal',
        3: 'suplementar',
        4: '13º salário'
    }

    def lista_todas_folhas_disponiveis(session):
        url_cookie = 'https://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={}'.format(str(options['<cliente>']).rjust(3, '0'))
        url_login = 'https://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
        url_lista_folhas = 'https://www.e-folha.sp.gov.br/desc_dempagto/pesqfolha.asp'
        r = s.get(url_cookie)
        form_data = {
          'txtMatricula': options['<usuario>'].rjust(6, '0'),
          'txtSenha': options['<senha>'],
          'txtNPA': '000000000',
          'btOK': 'ENTRAR'
        }
        r = s.post(url_login, data = form_data, cookies = r.cookies)
        r = s.get(url_lista_folhas, cookies = r.cookies)
        b = BeautifulSoup(r.text)
        table = b.find_all('table', attrs = {'class':'tabela'})
        pdfs = table[0].find_all('img', attrs = {'alt':'pdf'})
        folhas = []
        for pdf in pdfs:
            valores = pdf['onclick'][10:-3].split('\',\'')

            tipo = int(valores[0])
            sequencia = valores[1]
            mesref = valores[2]
            anoref = valores[3]

            detalhes = {
                'Folha': 'Folha ref {}/{} tipo {}'.format(mesref, anoref, enum_tipo[tipo]),
                'Tipo': tipo,
                'sequencia': sequencia,
                'mesref': mesref,
                'anoref': anoref,
                'arquivo': '{}_{}-Pagamentox-{}.pdf'.format(anoref, mesref, enum_tipo[tipo])
            }

            folhas.append(detalhes)
        return folhas, r.cookies

    def download_folha(session, folha_dict, cookie):
        url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'
        local_filename = folha_dict['arquivo']
        log('Fazendo o download da folha {}'.format(folha_dict['Folha']))

        # NOTE the stream=True parameter
        r = session.get(url, stream = True, data = folha_dict, cookies = cookie)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return local_filename

    s = requests.session()

    folhas, cookie = lista_todas_folhas_disponiveis(s)

    if options['--todas']:
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                download_folha(s, folha, cookie)
    elif options['-a'] or options['-m']:
        if options['-a']:
            folhas = [ folha for folha in folhas if folha['anoref'] == str(options['-a']) ]
        if options['-m']:
            folhas = [ folha for folha in folhas if folha['mesref'] == str(options['-m']).rjust(2, '0') ]
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                download_folha(s, folha, cookie)
    elif options['--ultima']:
        ultimo_mes = folhas[0]['mesref']
        ultimo_ano = folhas[0]['anoref']
        folhas = [ folha for folha in folhas if folha['mesref'] == ultimo_mes and folha['anoref'] == ultimo_ano ]
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                download_folha(s, folha, cookie)
    else:
        folhas = [ folha for folha in folhas if folha['mesref'] == str(datetime.datetime.now().month).rjust(2, '0') and folha['anoref'] == str(datetime.datetime.now().year) ]
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                download_folha(s, folha, cookie)

    log('Finalizado')

if __name__ == '__main__':
    main()