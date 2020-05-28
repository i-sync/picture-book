#!/usr/bin/env python3
# -*- coding: utf-8-*-

import os
import re
import json

INDEX_PATH = '/var/picture-book/www/data/xmly-books.json'
ROOT_PATH = '/mnt/sda1/xmly-huiben'
#INDEX_PATH = 'c:/source/python/picture-book/www/data/xmly-books.json'


def rename_folder():
    books = []
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        books = json.load(f)

    for book in books:
        source_folder = f"{ROOT_PATH}/{book['recordTitle']}"
        if not os.path.exists(source_folder):
            print(f"Source: [{source_folder}] don't exists , SKIP!!!")
            continue

        dest_folder = f"{ROOT_PATH}/{book['recordId']}.{book['recordTitle']}"

        if not os.path.exists(source_folder):
            print(f"Dest: [{source_folder}] exists , SKIP!!!")
            continue

        print(source_folder, dest_folder)
        #os.rename(source_folder, dest_folder)
        break


if __name__ == '__main__':
    rename_folder()