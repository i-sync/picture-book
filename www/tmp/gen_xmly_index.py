#!/usr/bin/env python3
# -*- coding: utf-8-*-

import os
import re
import json

#ROOT_PATH = '/mnt/sda1/xmly-huiben'
#INDEX_PATH = '/var/picture-book/www/data/xmly-books.json'
#ALBUM_PATH = '/var/picture-book/www/data/xmly-albums.json'

ROOT_PATH = 'c:/source/python/picture-book/www/data/xmly-json'
INDEX_PATH = 'c:/source/python/picture-book/www/data/xmly-books.json'
ALBUM_PATH = 'c:/source/python/picture-book/www/data/xmly-albums.json'

def gen_index_data():
    # check file path
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)

    if os.path.exists(ALBUM_PATH):
        os.remove(ALBUM_PATH)

    albums = []
    books = []
    for root, dirs, files in os.walk(ROOT_PATH):
        # print(root)
        for data in files:
            if data.endswith('.json'):
                with open(f'{root}/{data}', 'r', encoding='utf-8') as f:
                    jd = json.load(f)['data']
                    books.extend(jd['recordList'])
                    jd.pop('recordList')
                    albums.append(jd)

    if len(albums):
        books = sorted(books, key=lambda s: s['albumId'], reverse=True)
        with open(INDEX_PATH, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(books, ensure_ascii=False))

        albums = sorted(albums, key=lambda s: s['albumId'], reverse=True)
        with open(ALBUM_PATH, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(albums, ensure_ascii=False))


if __name__ == '__main__':
    gen_index_data()