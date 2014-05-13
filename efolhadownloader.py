#!/usr/bin/env python
#coding: utf-8

from docopt import docopt

doc = """Usage:
    efolhadownloader.py -c <cliente> -u <usuario> -s <senha> ([-a <ano> -m <mes>] | [-t] | [--ultima])

Options:
    -c <cliente>, --cliente 
    -u <usuario>, --usuario
    -s <senha>
    -a ANO, --ano ANO     Ano de referência
    -m MES, --mes MES     Mês de referência
    -t, --todas           Fazer o download de TODAS as folhas
    --ultima              Fazer o download da última folha disponível
"""
options = docopt(doc)
from pprint import pprint
pprint(options)
exit(0)

import requests
from bs4 import BeautifulSoup
import codecs
import argparse
import datetime
from pprint import pprint

enum_tipo = {
    1: "normal",
    3: "suplementar",
    4: "13º salário"
}

# parser = argparse.ArgumentParser(description="Faz o download do PDF da folha de pagamento especificada")

# parser.add_argument("-c", "--cliente", help="Cliente ALESP=50 Tribunal de Justica 21", choices=[21, 50], type=int, required=True)

# group = parser.add_argument_group()
# group.add_argument("-u", "--usuario", help="Usuário (matrícula)", required=True)
# group.add_argument("-s", "--senha", help="Senha", required=True)

# group2 = parser.add_argument_group()
# group2.add_argument("-a", "--ano", type=int, help="Ano de referência")
# group2.add_argument("-m", "--mes", type=int, help="Mês de referência")
# group2.add_argument("-t", "--todas", help="Fazer o download de TODAS as folhas", action="store_true")
# group2.add_argument("--ultima", help="Fazer o download da última folha disponível", action="store_true", default=False)

# parser.add_argument("-l", "--listar", help="Apenas listar quais folhas seriam baixadas", action="store_true", default=False)

# group3 = parser.add_mutually_exclusive_group()
# group3.add_argument("-v", "--verbose", help="Verbose (default)", action="store_const", dest="verbose", const=True, default=True)
# group3.add_argument("-q", "--quiet", help="Quiet", action="store_const", dest="verbose", const=False)

# args = parser.parse_args()

#if not args.mes:
#    args.mes = datetime.datetime.now().month

#if not args.ano:
#    args.ano = datetime.datetime.now().year

def lista_todas_folhas_disponiveis(session):
    url_cookie = 'https://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={}'.format(str(args.cliente).rjust(3, "0"))
    url_login = 'https://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
    url_lista_folhas = 'https://www.e-folha.sp.gov.br/desc_dempagto/pesqfolha.asp'
    r = s.get(url_cookie)
    form_data = {
      "txtMatricula": args.usuario.rjust(6, "0"),
      "txtSenha": args.senha,
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
        #print(pdf['onclick'][10:-3])
        #print(valores)
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
    if args.verbose:
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
#pprint(folhas)

if args.todas:
    for folha in folhas:
        if args.listar:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
elif args.ano or args.mes:
    if args.ano:
        folhas = [ folha for folha in folhas if folha["anoref"] == str(args.ano) ]
    if args.mes:
        folhas = [ folha for folha in folhas if folha["mesref"] == str(args.mes).rjust(2, "0") ]
    for folha in folhas:
        if args.listar:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
elif args.ultima:
    ultimo_mes = folhas[0]["mesref"]
    ultimo_ano = folhas[0]["anoref"]
    folhas = [ folha for folha in folhas if folha["mesref"] == ultimo_mes and folha["anoref"] == ultimo_ano ]
    for folha in folhas:
        if args.listar:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
else:
    folhas = [ folha for folha in folhas if folha["mesref"] == str(datetime.datetime.now().month).rjust(2, "0") and folha["anoref"] == str(datetime.datetime.now().year) ]
    for folha in folhas:
        if args.listar:
            pprint(folha)
        else:
            download_folha(s, folha, cookie)
