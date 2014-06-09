#!/usr/bin/python
#coding: utf-8
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
    if force:
        _datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pprint(_datetime + ' - ' + str(message))

def build_dict(arguments):
    return {
        'cliente': arguments['<cliente>'],
        'usuario': arguments['<usuario>'],
        'senha': arguments['<senha>']
    }
