#!/usr/bin/env python3
# -*- coding: utf-8-*-

import os
import re
import json

#ROOT_PATH = '/mnt/sda1/xmly-huiben'
ROOT_PATH = '/media/Study/yaya-huiben'
#INDEX_PATH = 'c:/source/python/picture-book/www/data/xmly-books.json'
INDEX_PATH = '/root/ximalaya/data/album-cover.json'


def update_album_cover():
    books = []
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        books = json.load(f)

    res = {}
    for book in books:
        book_id = book['id']
        res[book_id] = book

    for folder_name in os.listdir(ROOT_PATH):
        folder_id = folder_name[:folder_name.find('.')]
        if int(folder_id) in res.keys():
            print(folder_name)
            detail_json_name = f"{ROOT_PATH}/{folder_name}/{folder_id}.resourceDetail.json"
            detail_obj = {}
            with open(detail_json_name, 'r', encoding='utf-8') as f:
                detail_obj = json.load(f)

            detail_obj['data']['resource']['cover'] = res[int(folder_id)]['cover']

            with open(detail_json_name, 'w', encoding='utf-8') as f:
                json.dump(detail_obj, f, ensure_ascii=False)
            #break

if __name__ == '__main__':
    update_album_cover()