#!/usr/bin/env python
#coding: utf-8

_enum_tipo = {
    1: u'normal',
    3: u'suplementar',
    4: u'13º salário'
}

NORMAL = _enum_tipo[1] #(1, u'normal')
SUPLEMENTAR = _enum_tipo[3] #(3, u'suplementar')
DECIMO_TERCEIRO = _enum_tipo[4] #(4, u'13º salário')

def from_int(value):
    return _enum_tipo[value]
