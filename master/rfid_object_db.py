#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
'''rfid_object_db.py: actions for rfid triggers'''
__author__ = 'Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)'
__copyright__ = '2017, MIT'

object_db = {
    'default': {
        'category': 'unknown',
        'title': 'Mystery Object',
        'key':  'default',
    },
    '02:52:70:48:48:49:48:48:65:54:54:51:51:03:3': {
        'title': 'Remote Control',
        'key':  'remote',
    },
    '02:52:70:48:48:49:48:52:68:56:68:57:70:03:3': {
        'title': 'Coin Purse',
        'key':  'purse',
    },
    '02:48:57:48:48:57:50:57:56:53:56:53:66:03:3': {
        'title': 'Playing Cards',
        'key':  'cards',
    },
    '02:49:56:48:48:50:57:54:67:69:49:66:67:03:3': {
        'title': 'Picture of Saints',
        'key':  'saints',
    },
    '02:51:48:48:48:51:55:51:49:65:57:57:70:03:3': {
        'title': 'Doorknob',
        'key':  'doorknob',
    },
}
