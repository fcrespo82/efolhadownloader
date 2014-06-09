#!/usr/bin/python
#coding: utf-8
'''
usage:
    efolhadownloader.py <command> [<args>...]

commands:
    config      Cria as configuracoes para acesso
    download    Faz o download das folhas de pagamento
    listar      Lista as folhas de pagamento

'''

__version__ = '0.6'

from docopt import docopt
import pprint

class EFolhaListar:
    pass

class EFolhaDownload:
    '''usage:
    efolhadownloader.py download [-a <a>]

options:
    -a <a>   ano
    '''

def main():
    args = docopt(__doc__,
                    version=__version__,
                    options_first=True)

    argv = [args['<command>']] + args['<args>']

    if args['<command>'] == 'config':
        import efd_common
        args = docopt(efd_common.__doc__, argv=argv)
    elif args['<command>'] == 'listar':
        args = docopt(EFolhaListar.__doc__, argv=argv)
    elif args['<command>'] == 'download':
        args = docopt(EFolhaDownload.__doc__, argv=argv)
    print args

if __name__ == '__main__':
    main()