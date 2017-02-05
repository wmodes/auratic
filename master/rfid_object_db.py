#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
"""rfid_object_db.py: actions for rfid triggers"""
__author__      = "Wes Modes (wmodes@gmail.com) & SL Benz (slbenzy@gmail.com)"
__copyright__   = "2017, MIT"

youtube_url = "https://www.youtube.com/embed/"
#youtube_url = "http://www.youtube.com/watch_popup?v="
#youtube_url = "https://www.youtube.com/tv#/watch?v="
#youtube_url = "https://www.youtube.com/watch?v="
youtube_post = "?rel=0&autoplay=1"

default_url = youtube_url + "OByCDlsk9jo" + youtube_post

object_db = {
    "default": {
        "id": 0, 
        "category": "unknown", 
        "title": "Mystery Object",
        "duration": 10,
        "video": "NaW43C6_Nc0"},
    "02:52:70:48:48:49:48:48:65:54:54:51:51:03:3": {
        "id": 1, 
        "category": "dishes", 
        "title": "whiskey cup", 
        "duration": 10,
        "video": "64xeIVQK7Vs"},
    "02:52:70:48:48:49:48:52:68:56:68:57:70:03:3": {
        "id": 2, 
        "category": "housewares", 
        "title": "candle", 
        "duration": 30,
        "video": "baadWmJKOjM"},
    "02:48:57:48:48:57:50:57:56:53:56:53:66:03:3": {
        "id": 3, 
        "category": "floral", 
        "title": "rose", 
        "duration": 10,
        "video": "baadWmJKOjM"},
    "02:49:56:48:48:50:57:54:67:69:49:66:67:03:3": {
        "id": 4, 
        "category": "housewares", 
        "title": "rubber ducky", 
        "duration": 5,
        "video": "baadWmJKOjM"},
    "02:51:48:48:48:51:55:51:49:65:57:57:70:03:3": {
        "id": 5, 
        "category": "fauna", 
        "title": "bluebird", 
        "duration": 30,
        "video": "baadWmJKOjM"}
    }

