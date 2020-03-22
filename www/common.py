#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import os
import json


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
    books = None
    labels = None
    ages = ['0-2岁', '2-4岁', '4-6岁', '6-8岁', '>=8岁']

    @classmethod
    def get_books(cls, id=None, age=None, labelid=None):
        if cls.books:
            if id:
                return [book for book in cls.books if int(id) == book['id']]
            if labelid and age:
                return [book for book in cls.books if int(labelid) in book['labelList'] and age == book['ageDesc']]
            elif labelid:
                return [book for book in cls.books if int(labelid) in book['labelList']]
            elif age:
                return [book for book in cls.books if age == book['ageDesc']]
            else:
                return cls.books
        json_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/books.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            cls.books = json.load(f)

        return cls.books

    @classmethod
    def get_labels(cls):
        if cls.labels:
            return cls.labels
        json_file = f'{os.path.dirname(os.path.abspath(__file__))}/data/labels.json'
        with open(json_file, 'r', encoding='utf-8') as f:
            cls.labels = json.load(f)['data']['labelList']

        return cls.labels
