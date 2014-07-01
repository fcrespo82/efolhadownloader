#!/usr/bin/env python
#coding: utf-8
'''
usage:
    efd.py <comando> [<args>...]

comandos:
    config      Cria as configuracoes para acesso
    download    Faz o download das folhas de pagamento
    listar      Lista as folhas de pagamento
'''

__version__ = '0.6'

from docopt import docopt
from pprint import pprint
import sys
from efolha import common

def main():
    args = docopt(__doc__,
                    version=__version__,
                    options_first=True)

    argv = [args['<comando>']] + args['<args>']

    common.log('Argumentos: {}'.format(argv), args)

    if args['<comando>'] == 'config':
        from efolha import config
        args = docopt(config.__doc__, argv=argv, options_first=False)
        config.save(args)
    elif args['<comando>'] == 'listar':
        from efolha import config, listar
        args = docopt(listar.__doc__, argv=argv, options_first=False)
        config = config.load(args)
        folhas, cookie = listar.folhas(config, args)
        map(pprint, folhas)
    elif args['<comando>'] == 'download':
        from efolha import listar, config, download
        args = docopt(download.__doc__, argv=argv, options_first=False)
        config = config.load(args)
        folhas, cookie = listar.folhas(config, args)
        for folha in folhas:
            #print folha, config
            download.folha(folha, cookie, args)
    else:
        print('Comando não identificado')
        print(__doc__)
    #print args

if __name__ == '__main__':
    main()