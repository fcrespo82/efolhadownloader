#!/usr/bin/env python
#coding: utf-8

import requests
import os
from bs4 import BeautifulSoup
from pprint import pprint

config = {'cliente': 50,
    'usuario': '23296',
    'senha': 'fern@ndo82',
    'output_dir': '/home/fxcrespo/developer/efolhadownloader'
}


Tipo = {
    1: u'normal',
    3: u'suplementar',
    4: u'13º salário'
}

NORMAL = Tipo[1] #(1, u'normal')
SUPLEMENTAR = Tipo[3] #(3, u'suplementar')
DECIMO_TERCEIRO = Tipo[4] #(4, u'13º salário')


def recupera_nome_e_cliente(session, folha_dict, cookie):
    url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagto.asp'
    # NOTE the stream=True parameter
    r = session.get(url, stream = True, data = folha_dict, cookies = cookie)
    bs = BeautifulSoup(r.text)
    cliente = bs.findAll('nobr')[0].text.strip()
    nome = bs.findAll('left')[1].text.strip()
    return nome.replace(u' ', u'_'), cliente.replace(u' ', u'_')


s = requests.session()
url_cookie = 'http://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={}'.format(str(config['cliente']).rjust(3, '0'))
url_login = 'http://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
url_lista_folhas = 'http://www.e-folha.sp.gov.br/desc_dempagto/Folhas.asp'
url_download = 'http://www.e-folha.sp.gov.br/desc_dempagto/DemPagtoP.asp'

r = s.get(url_cookie)
form_data = {
  'txtMatricula': config['usuario'].rjust(6, '0'),
  'txtSenha': config['senha'],
  'txtNPA': '000000000',
  'btOK': 'ENTRAR'
}

cookies = r.cookies
r = s.post(url_login, data = form_data, cookies = cookies)

r = s.post(url_lista_folhas, cookies = cookies)

b = BeautifulSoup(r.text)
table = b.find_all('table', attrs = {'class':'tabela'})
pdfs = table[0].find_all('img', attrs = {'alt':'pdf'})
folhas = []
nome = ''
cliente = ''

for pdf in pdfs:
    valores = pdf['onclick'][10:-3].split('\',\'')

    _tipo = str(int(valores[0]))
    _sequencia = str(valores[1]).rjust(2, '0')
    _mesref = str(valores[2]).rjust(2, '0')
    _anoref = str(valores[3])

    detalhes = {
        u'Folha': u'Folha ref {0}/{1} tipo {2}'.format(_mesref, _anoref, Tipo[int(_tipo)]),
        u'Tipo': _tipo,
        u'sequencia': _sequencia,
        u'mesref': _mesref,
        u'anoref': _anoref,
        u'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{2}.pdf'.format(_anoref, _mesref, Tipo[int(_tipo)], nome, cliente)
    }

    if nome == '' or cliente == '':
        nome, cliente = recupera_nome_e_cliente(s, detalhes, cookies)

    detalhes.update({
        u'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{5}_{2}.pdf'.format(_anoref, _mesref, Tipo[int(_tipo)], nome, cliente, _sequencia),
        u'nome': nome,
        u'cliente': cliente
    })

    folhas.append(detalhes)

# folha_dict = {
#     #u'Folha': u'Folha ref {0}/{1} tipo {2}'.format(_mesref, _anoref, tipo.Tipo[_tipo)),
#     u'Tipo': '1',
#     u'sequencia': '01',
#     u'mesref': '05',
#     u'anoref': '2014'
#     # u'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{2}.pdf'.format(_anoref, _mesref, tipo.Tipo[_tipo), nome, cliente)
# }

# Tipo=1
# anoref=2014
# mesref=09
# sequencia=01
# strTarget=mostraDP
#
# for c in cookies:
#     print(c)
#
# print(url_download)
# print(folha_dict)
# print(cookies)

for folha in folhas:
    r = s.post(url_download, stream = True, data = folha, cookies = cookies)

    full_path_download= '/'.join([config['output_dir'], folha['arquivo']])

    if not os.path.exists(full_path_download):
        print('downloading')
        with open(full_path_download, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
