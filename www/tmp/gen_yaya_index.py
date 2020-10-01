#!/usr/bin/env python3
# -*- coding: utf-8-*-

import os
import re
import json
from ..utils import fixed_file_name

ROOT_PATH = '/mnt/sda1/yaya-huiben'
INDEX_PATH = '/var/picture-book/www/data/yaya-books.json'


def gen_index_data():
    # check file path
    if os.path.exists(INDEX_PATH):
        os.remove(INDEX_PATH)

    res = []
    for root, dirs, files in os.walk(ROOT_PATH):
        # print(root)
        if len(dirs) + len(files) != 6:
            continue
        for data in files:
            if data.endswith('resourceDetail.json'):
                with open(f'{root}/{data}', 'r', encoding='utf-8') as f:
                    jd = json.load(f)['data']['resource']
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