#!/usr/bin/python
#coding: utf-8
'''
usage:
    efolhadownloader.py <comando> [<args>...]

comandos:
    config      Cria as configuracoes para acesso
    download    Faz o download das folhas de pagamento
    listar      Lista as folhas de pagamento

'''

__version__ = '0.6'

from docopt import docopt
import pprint

def main():
    args = docopt(__doc__,
                    version=__version__,
                    options_first=True)

    argv = [args['<comando>']] + args['<args>']

    if args['<comando>'] == 'config':
        import efd_config
        args = docopt(efd_config.__doc__, argv=argv, options_first=True)
        efd_config.save_config(args)
    elif args['<comando>'] == 'listar':
        import efd_config, efd_listar
        args = docopt(efd_listar.__doc__, argv=argv, options_first=True)
        efd_config.return_config(args)
    elif args['<comando>'] == 'download':
        import efd_config, efd_download
        args = docopt(efd_download.__doc__, argv=argv, options_first=True)
    else:
        print('Comando não identificado')
        print(__doc__)
    print args

if __name__ == '__main__':
    main()