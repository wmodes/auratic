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
    #'02:52:69:48:48:66:48:49:48:65:48:52:69:03': {
    '00:00:01:01:05:03:08:05:09:02': {
        'title': 'Remote Control',
        'key':  'remote',
    },
    #'02:52:69:48:48:65:70:70:54:57:48:56:55:03': {
    '00:00:01:01:05:03:01:09:02:00': {
        'title': 'Hair Tie',
        'key':  'hair',
    },
    '02:52:70:48:48:49:48:50:50:50:56:53:53:03': {
        'title': 'Coin Purse',
        'key':  'purse',
    },
    '02:52:70:48:48:49:48:50:67:69:68:57:69:03': {
        'title': 'Playing Cards',
        'key':  'cards',
    },
    '02:52:69:48:48:65:70:66:67:69:50:66:70:03': {
        'title': 'Playing Cards',
        'key':  'cards',
    },
    '02:49:56:48:48:50:57:54:67:69:49:66:67:03': {
        'title': 'Picture of Saints',
        'key':  'saints',
    },
    '02:52:69:48:48:65:70:70:54:57:48:56:56:03': {
        'title': 'Doorknob',
        'key':  'doorknob',
    },
    #'02:52:69:48:48:65:70:69:56:70:70:70:54:03': {
    '00:00:01:01:05:02:08:04:04:07': {
        'title': 'Phone',
        'key':  'phone',
    },
}
