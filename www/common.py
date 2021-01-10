#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import re
import os
import json

from utils import get_cdn_url

class Dict(dict):
    '''
    Simple dict but support access as x.y style.
    '''

    def __init__(self, names=(), values=(), **kwargs):
        super(Dict, self).__init__(**kwargs)

        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '{}'".format(key))

    def __setattr__(self, key, value):
        self[key] = value


def toDict(d):
    D = Dict()
    for k, v in d.items():
        D[k] = toDict(v) if isinstance(v, dict) else v
    return D


def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v

    return r


class DataObject:
    yaya_books = None
    xmly_books = None
    xmly_albums = None
    labels = None
    ages = ['0-2岁', '2-4岁', '4-6岁', '6-8岁', '>=8岁']

    @classmethod
    def get_yaya_books(cls, id=None, age=None, labelid=None):
        if cls.yaya_books:
            if id:
                return [book for book in cls.yaya_books if int(id) == book['id']]
            if labelid and age:
                return [book for book in cls.yaya_books if int(labelid) in book['labelList'] and age == book['ageDesc']]
            elif labelid:
                return [book for book in cls.yaya_books if int(labelid) in book['labelList']]
            elif age:
                return [book for book in cls.yaya_books if age == book['ageDesc']]
            else:
                return cls.yaya_books
        json_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/yaya-books.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            cls.yaya_books = json.load(f)

        return cls.yaya_books

    @classmethod
    def get_xmly_books(cls, id=None, albumid=None):
        if cls.xmly_books:
            if id:
                return [book for book in cls.xmly_books if int(id) == book['recordId']]
            elif albumid:
                return [book for book in cls.xmly_books if int(albumid) == book['albumId']]
            else:
                return cls.xmly_books
        json_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/xmly-books.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            cls.xmly_books = json.load(f)

        return cls.xmly_books

    @classmethod
    def get_xmly_albums(cls, id=None):
        if cls.xmly_albums:
            if id:
                return [album for album in cls.xmly_albums if int(id) == album['albumId']]
            else:
                return cls.xmly_albums
        json_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/xmly-albums.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            cls.xmly_albums = json.load(f)

        return cls.xmly_albums

    @classmethod
    def get_labels(cls):
        if cls.labels:
            return cls.labels
        json_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/labels.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            cls.labels = json.load(f)['data']['labelList']

        return cls.labels
