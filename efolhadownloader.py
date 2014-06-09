#!/usr/bin/env python
#coding: utf-8

from bs4 import BeautifulSoup
from docopt import docopt
from pprint import pprint
from subprocess import Popen, PIPE
import datetime
import json
import md5
import os
import requests
import shlex

__version__ = '0.6'

#efolhadownloader.py download ((-a <a> -m <m>) | --todas | --ultima) [--diretorio <dir> --nome_base <arquivo> --download_dir <down_dir> --listar --forcar --verbose]
__doc__ = '''usage:

    efolhadownloader.py download ((-a <a> -m <m>) | -tu) [--diretorio <dir> --nome_base <arquivo> --download_dir <down_dir> -lfv]
    efolhadownloader.py cria_config <cliente> <usuario> <senha> [--diretorio <dir> --nome_base <arquivo> -v]
    efolhadownloader.py --version
    efolhadownloader.py -h

cria_config options:
    <cliente>                    Cliente
    <usuario>                    Matrícula
    <senha>                      Senha

download options:
    -a <a>                       Ano de referência
    -m <m>                       Mês de referência
    -t --todas                   Fazer o download de TODAS as folhas
    -u --ultima                  Fazer o download da última folha disponível
    -l --listar                  Apenas lista as folhas (NÃO faz download)
    -f --forcar                  Faz download mesmo se o arquivo já existir [default: False]

common options:
    --nome_base <arquivo>        Nome do arquivo para ler/salvar as configurações e chave de criptografia [default: efolha]
    -v --verbose                 Informa o que o programa está fazendo
    --diretorio <dir>            Diretorio para buscar os arquivos de chave e configurações [default: .]
    --download_dir <down_dir>    Diretório para downloads dos arquivos [default: .]
'''
options = docopt(__doc__, version=__version__)
print(options)
def main():
    def encrypt(password, text):
        _command=shlex.split(u'openssl enc -aes-256-cbc -e -a -pass')
        _command.append(u'pass:' + password)
        po = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = po.communicate(text)
        return stdout #{u'stdout': stdout, u'error': stderr, u'return_code': po.returncode }

    def decrypt(password, text):
        _command=shlex.split(u'openssl enc -aes-256-cbc -d -a -pass')
        _command.append(u'pass:' + password)
        po = Popen(_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = po.communicate(text)
        return stdout #{u'stdout': stdout, u'error': stderr, u'return_code': po.returncode }

    def log(message, force=False):
        if options['--verbose'] or force:
            _datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            pprint(_datetime + ' - ' + str(message))

    def full_path(path, filename):
        return os.path.realpath(os.path.expanduser(os.path.join(path, filename)))

    log(u'Iniciando')
    if options['cria_config']:
        log(u'Criando hash dos dados de entrada')
        _hash = md5.new(options['<cliente>'])
        _hash.update(options['<usuario>'])
        _hash.update(options['<senha>'])
        key = _hash.hexdigest()
        log(u'Hash: {}'.format(key))
        _dir = options['--diretorio']
        log(u'Salvando hash no arquivo {}'.format(options['--nome_base']+".key"))
        full_path_key = full_path(_dir, options['--nome_base']+".key")
        log(u'Caminho completo \'{}\''.format(full_path_key))
        with open(full_path_key, 'wb') as key_file:
            key_file.write(key)

        config = {
            'cliente': options['<cliente>'],
            'usuario': options['<usuario>'],
            'senha': options['<senha>']
        }

        log(u'Encriptando dados de entrada')
        encrypted = encrypt(key, json.dumps(config))
        _dir = options['--diretorio']
        log(u'Salvando dados encriptados no arquivo {}'.format(options['--nome_base']+".config"))
        full_path_config = full_path(_dir, options['--nome_base']+".config")
        log(u'Caminho completo \'{}\''.format(full_path_config))
        with open(full_path_config, 'wb') as config_file:
            config_file.write(encrypted)
        log(u'Finalizado\n')
        exit(0)
    elif options['download']:
        _dir = options['--diretorio']
        log(u'Carregando dados do arquivo {}'.format(options['--nome_base']+".config"))
        full_path_config = full_path(_dir, options['--nome_base']+".config")
        log(u'Caminho completo \'{}\''.format(full_path_config))
        with open(full_path_config, 'rb') as config_file:
            file_data=config_file.readlines()
            encrypted = ''.join(file_data)
        log(u'Desencriptando dados com a chave contida no arquivo'.format(options['--nome_base']+".key"))
        full_path_key = full_path(_dir, options['--nome_base']+".key")
        log(u'Caminho completo \'{}\''.format(full_path_key))
        with open(full_path_key,'rb') as key_file:
            key = ''.join(key_file.readlines())
        decrypted = decrypt(key, encrypted)
        config = json.loads(decrypted)

        options['<cliente>'] = config['cliente']
        options['<usuario>'] = config['usuario']
        options['<senha>'] = config['senha']
        log(u'Dados carregados')

    enum_tipo = {
        1: u'normal',
        3: u'suplementar',
        4: u'13º salário'
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
        nome = ''
        cliente = ''
        for pdf in pdfs:
            valores = pdf['onclick'][10:-3].split('\',\'')

            tipo = int(valores[0])
            sequencia = valores[1]
            mesref = valores[2]
            anoref = valores[3]

            detalhes = {
                'Folha': u'Folha ref {0}/{1} tipo {2}'.format(mesref, anoref, enum_tipo[tipo]),
                'Tipo': tipo,
                'sequencia': sequencia,
                'mesref': mesref,
                'anoref': anoref,
                'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{2}.pdf'.format(anoref, mesref, enum_tipo[tipo], nome, cliente)
            }

            if nome == '' or cliente == '':
                nome, cliente = recupera_nome_e_cliente(s, detalhes, r.cookies)

            detalhes = {
                'Folha': u'Folha ref {0}/{1} tipo {2}'.format(mesref, anoref, enum_tipo[tipo]),
                'Tipo': tipo,
                'sequencia': sequencia,
                'mesref': mesref,
                'anoref': anoref,
                'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{2}.pdf'.format(anoref, mesref, enum_tipo[tipo], nome, cliente)
            }

            folhas.append(detalhes)
        return folhas, r.cookies

    def recupera_nome_e_cliente(session, folha_dict, cookie):
        url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagto.asp'
        # NOTE the stream=True parameter
        r = session.get(url, stream = True, data = folha_dict, cookies = cookie)
        bs = BeautifulSoup(r.text)
        cliente = bs.findAll('nobr')[0].text.strip()
        nome = bs.findAll('left')[1].text.strip()
        return nome.replace(u' ', u'_'), cliente.replace(u' ', u'_')

    def file_exists(folha_dict):
        _dir = options['--download_dir']
        _full_path = full_path(_dir, folha_dict['arquivo'])
        return os.path.exists(_full_path)

    def download_folha(session, folha_dict, cookie):
        url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'

        local_filename = folha_dict['arquivo']
        log(u'Fazendo o download da folha {}'.format(folha_dict['Folha']))

        # NOTE the stream=True parameter
        r = session.get(url, stream = True, data = folha_dict, cookies = cookie)
        _dir = options['--download_dir']
        full_path_download = full_path(_dir, local_filename)
        log(u'Caminho completo \'{}\''.format(full_path_download.encode('ascii', 'ignore')))
        with open(full_path_download, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return full_path_download

    s = requests.session()

    folhas, cookie = lista_todas_folhas_disponiveis(s)
    #nome, cliente = recupera_nome_e_cliente(s, folhas[0], cookie)

    if options['--todas']:
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                if not file_exists or options['--forcar']:
                    download_folha(s, folha, cookie)
                else:
                    log("O arquivo já existe no destino", True)
    elif options['-a'] or options['-m']:
        if options['-a']:
            folhas = [ folha for folha in folhas if folha['anoref'] == str(options['-a']) ]
        if options['-m']:
            folhas = [ folha for folha in folhas if folha['mesref'] == str(options['-m']).rjust(2, '0') ]
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                if not file_exists or options['--forcar']:
                    download_folha(s, folha, cookie)
                else:
                    log("O arquivo já existe no destino", True)
    elif options['--ultima']:
        ultimo_mes = folhas[0]['mesref']
        ultimo_ano = folhas[0]['anoref']
        folhas = [ folha for folha in folhas if folha['mesref'] == ultimo_mes and folha['anoref'] == ultimo_ano ]
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                if not file_exists or options['--forcar']:
                    download_folha(s, folha, cookie)
                else:
                    log("O arquivo já existe no destino", True)
    else:
        folhas = [ folha for folha in folhas if folha['mesref'] == str(datetime.datetime.now().month).rjust(2, '0') and folha['anoref'] == str(datetime.datetime.now().year) ]
        for folha in folhas:
            if options['--listar']:
                log(folha, True)
            else:
                if not file_exists or options['--forcar']:
                    download_folha(s, folha, cookie)
                else:
                    log("O arquivo já existe no destino", True)

    log(u'Finalizado')

if __name__ == '__main__':
    main()
