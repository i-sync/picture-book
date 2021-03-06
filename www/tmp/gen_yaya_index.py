#!/usr/bin/env python3
# -*- coding: utf-8-*-

import sys
import os
import re
import json

ROOT_PATH = '/var/www/picture-book/www/files/yaya-huiben'
INDEX_PATH = '/var/www/picture-book/www/data/yaya-books.json'

exclude_ids = [
    2598,
    2599,
    2600,
    2601,
    2602,
    2603,
    2604,
    2605,
    2606,
    2607,
    2969,
    2970,
    2971,
    2972,
    3062,
    3063,
    3064,
    3065,
    3066,
    3164,
    3165,
    3278,
    3279,
    3280,
    3281
]

def fixed_file_name(file_name: str):
    file_name = re.sub(r'\s', '-', file_name)
    file_name = re.sub(r'[^\w\-_\. ]', '-', file_name)
    file_name = re.sub(r'-{2,}', '-', file_name)
    return file_name.strip('-')

def gen_index_data():
    # check file path
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)

    res = []
    for root, dirs, files in os.walk(ROOT_PATH):
        # print(root)
        if len(dirs) + len(files) != 3:
            continue
        for data in files:
            if data.endswith('resourceDetail.json'):
                with open(f'{root}/{data}', 'r', encoding='utf-8') as f:
                    jd = json.load(f)['data']['resource']

                if jd['id'] in exclude_ids:
                    break
                ds = {}
                ds['ageDesc'] = jd['ageDesc']
                ds['cover'] = jd['cover'].replace('http://', '//').replace('.png', '_%s.png')
                ds['id'] = jd['id']
                ds['name'] = fixed_file_name(jd['name'])
                ds['labelList'] = [la['id'] for la in jd['labelList']]
                ds['totalChapter'] = jd['totalChapter']
                res.append(ds)
                break

    if len(res):
        res = sorted(res, key=lambda s: s['id'], reverse=True)
        with open(INDEX_PATH, 'w+', encoding='utf-8') as f:
            f.write(json.dumps(res, ensure_ascii=False))


if __name__ == '__main__':
    gen_index_data()