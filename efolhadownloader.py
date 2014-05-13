#!/usr/bin/env python
#coding: utf-8

from docopt import docopt
import sys
from pprint import pprint
import requests
from bs4 import BeautifulSoup
import codecs
import datetime
import json
from base64 import b64encode, b64decode

doc = """Usage:   
    efolhadownloader.py -c <c> -u <u> -s <s> ((-a <a> -m <m>) | --todas | --ultima) [--listar] [--verbose]
    efolhadownloader.py --config <arquivo> ((-a <a> -m <m>) | --todas | --ultima) [--listar] [--verbose]
    efolhadownloader.py cria_config -c <c> -u <u> -s <s> [--saida <arquivo>]

Login options:
    -c <c>                  Cliente
    -u <u>                  Matrícula
    -s <s>                  Senha
    --config <arquivo>      Ler usuario senha e cliente do <arquivo>

Download options:
    -a <a>                  Ano de referência
    -m <m>                  Mês de referência
    --todas                 Fazer o download de TODAS as folhas
    --ultima                Fazer o download da última folha disponível

General options:
    --listar                Apenas lista as folhas (NÃO faz download)
    --verbose               Informa o que o programa está fazendo
    --saida <arquivo>       Nome do arquivo para salvar as configurações [default: efolha.config]
"""
options = docopt(doc)

if options['cria_config']:
    config = {
        'cliente': b64encode(options['-c']),
        'usuario': b64encode(options['-u']),
        'senha': b64encode(options['-s'])
    }
    with open(options['--saida'], "w") as f:
        f.write(b64encode(json.dumps(config)))
    exit(0)
elif options['--config']:
    with open(options['--config'], "r") as f:
        file_data=f.readlines()
        data = b64decode("".join(file_data))
        config = json.loads(data)

    config = {
        'cliente': b64decode(config['cliente']),
        'usuario': b64decode(config['usuario']),
        'senha': b64decode(config['senha'])
    }

    options['-c'] = config['cliente']
    options['-u'] = config['usuario']
    options['-s'] = config['senha']

enum_tipo = {
    1: "normal",
    3: "suplementar",
    4: "13º salário"
}

def lista_todas_folhas_disponiveis(session):
    url_cookie = 'https://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={}'.format(str(options['-c']).rjust(3, "0"))
    url_login = 'https://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
    url_lista_folhas = 'https://www.e-folha.sp.gov.br/desc_dempagto/pesqfolha.asp'
    r = s.get(url_cookie)
    form_data = {
      "txtMatricula": options['-u'].rjust(6, "0"),
      "txtSenha": options['-s'],
      "txtNPA": "000000000",
      "btOK": "ENTRAR"
    }
    r = s.post(url_login, data = form_data, cookies = r.cookies)
    r = s.get(url_lista_folhas, cookies = r.cookies)
    b = BeautifulSoup(r.text)
    table = b.find_all('table', attrs = {'class':'tabela'})
    pdfs = table[0].find_all("img", attrs = {'alt':'pdf'})
    folhas = []
    for pdf in pdfs:
        valores = pdf['onclick'][10:-3].split("','")

        tipo = int(valores[0])
        sequencia = valores[1]
        mesref = valores[2]
        anoref = valores[3]

        detalhes = {
            "Folha": "Folha ref {}/{} tipo {}".format(mesref, anoref, enum_tipo[tipo]),
            "Tipo": tipo,
            "sequencia": sequencia,
            "mesref": mesref,
            "anoref": anoref,
            "arquivo": "{}_{}-Pagamentox-{}.pdf".format(anoref, mesref, enum_tipo[tipo])
        }

        folhas.append(detalhes)
    return folhas, r.cookies

def download_folha(session, folha_dict, cookie):
    url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'
    local_filename = folha_dict["arquivo"]
    # NOTE the stream=True parameter
    if options['--verbose']:
        print("Fazendo o download da folha {}".format(folha_dict["Folha"]))

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
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
elif options['-a'] or options['-m']:
    if options['-a']:
        folhas = [ folha for folha in folhas if folha["anoref"] == str(options['-a']) ]
    if options['-m']:
        folhas = [ folha for folha in folhas if folha["mesref"] == str(options['-m']).rjust(2, "0") ]
    for folha in folhas:
        if options['--listar']:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
elif options['--ultima']:
    ultimo_mes = folhas[0]["mesref"]
    ultimo_ano = folhas[0]["anoref"]
    folhas = [ folha for folha in folhas if folha["mesref"] == ultimo_mes and folha["anoref"] == ultimo_ano ]
    for folha in folhas:
        if options['--listar']:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
else:
    folhas = [ folha for folha in folhas if folha["mesref"] == str(datetime.datetime.now().month).rjust(2, "0") and folha["anoref"] == str(datetime.datetime.now().year) ]
    for folha in folhas:
        if options['--listar']:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
