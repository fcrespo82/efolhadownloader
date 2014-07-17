#!/usr/bin/env python
#coding: utf-8
'''
usage:
    efd.py listar ((<a> <m>) | -t | -u) [-d <dir> -p <arquivo> -s <dir> -v]

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

import requests
from bs4 import BeautifulSoup
import tipo
from efolha import common

def folhas(config, arguments):
    common.log(u'Listando folhas', arguments)
    s = requests.session()
    url_cookie = 'https://www.e-folha.sp.gov.br/desc_dempagto/entrada.asp?cliente={}'.format(str(config['cliente']).rjust(3, '0'))
    url_login = 'https://www.e-folha.sp.gov.br/desc_dempagto/PesqSenha.asp'
    url_lista_folhas = 'https://www.e-folha.sp.gov.br/desc_dempagto/pesqfolha.asp'
    r = s.get(url_cookie)
    form_data = {
      'txtMatricula': config['usuario'].rjust(6, '0'),
      'txtSenha': config['senha'],
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

        _tipo = int(valores[0])
        _sequencia = valores[1]
        _mesref = valores[2]
        _anoref = valores[3]

        detalhes = {
            u'Folha': u'Folha ref {0}/{1} tipo {2}'.format(_mesref, _anoref, tipo.from_int(_tipo)),
            u'Tipo': _tipo,
            u'sequencia': _sequencia,
            u'mesref': _mesref,
            u'anoref': _anoref,
            u'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{2}.pdf'.format(_anoref, _mesref, tipo.from_int(_tipo), nome, cliente)
        }

        if nome == '' or cliente == '':
            nome, cliente = recupera_nome_e_cliente(s, detalhes, r.cookies, arguments)

        detalhes.update({
            u'arquivo': u'{0}_{1}-Pagamentox-{3}-{4}_{5}_{2}.pdf'.format(_anoref, _mesref, tipo.from_int(_tipo), nome, cliente, _sequencia),
            u'nome': nome,
            u'cliente': cliente
        })

        folhas.append(detalhes)

        if arguments['<a>'] or arguments['<m>']:
            if arguments['<a>']:
                folhas = [ folha for folha in folhas if folha['anoref'] == str(arguments['<a>']) ]
            if arguments['<m>']:
                folhas = [ folha for folha in folhas if folha['mesref'] == str(arguments['<m>']).rjust(2, '0') ]
        elif arguments['--ultima']:
            ultimo_mes = folhas[0]['mesref']
            ultimo_ano = folhas[0]['anoref']
            folhas = [ folha for folha in folhas if folha['mesref'] == ultimo_mes and folha['anoref'] == ultimo_ano ]

    return folhas, r.cookies

def recupera_nome_e_cliente(session, folha_dict, cookie, arguments):
    common.log(u'Buscando dados de nome e cliente para as folhas', arguments)
    url = 'https://www.e-folha.sp.gov.br/desc_dempagto/DemPagto.asp'
    # NOTE the stream=True parameter
    r = session.get(url, stream = True, data = folha_dict, cookies = cookie)
    bs = BeautifulSoup(r.text)
    cliente = bs.findAll('nobr')[0].text.strip()
    nome = bs.findAll('left')[1].text.strip()
    return nome.replace(u' ', u'_'), cliente.replace(u' ', u'_')