#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import re
import os
import time
import json
import string
import hashlib
import random
import requests
import urllib.parse
from config import configs


def fixed_file_name(file_name: str):
    file_name = re.sub(r'\s', '-', file_name)
    file_name = re.sub(r'[^\w\-_\. ]', '-', file_name)
    file_name = re.sub(r'-{2,}', '-', file_name)
    return file_name.strip('-')


def get_cdn_url(path):
    '''
    Get cdn url
    :param cls:
    :param path:
    :return:
    '''
    timestamp = round(time.time())
    rand = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(20, 30)))
    uid = 0
    md5hash = hashlib.md5(f"{urllib.parse.quote(path)}-{timestamp}-{rand}-{uid}-{configs.cdn.secret}".encode('utf-8')).hexdigest()
    return f"https://cdn.picture.viagle.com{urllib.parse.quote(path)}?sign={timestamp}-{rand}-{uid}-{md5hash}"


def verify_sign(path, sign):
    #print(f"===================> {path}, {sign}")
    if not path or not sign or sign.count('-') != 3:
        return False
    timestamp, rand, uid, md5hash = sign.split('-')
    return md5hash == hashlib.md5(f"{urllib.parse.quote(path)}-{timestamp}-{rand}-{uid}-{configs.cdn.secret}".encode('utf-8')).hexdigest()


def read_json_file(cls, file_path):
    json_file = f'{os.path.dirname(os.path.abspath(__file__))}/files{file_path}'
    if not os.path.exists(json_file):
        #download json file form cdn
        if not os.path.exists(os.path.dirname(json_file)):
            os.makedirs(os.path.dirname(json_file))
        file_url = get_cdn_url(file_path)
        res = requests.get(file_url)
        if res.status_code == requests.codes.ok:
            with open(json_file, 'w+', encoding='utf-8') as f:
                f.write(res.content)

    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    key = "/xmly-books/3340428000.%E5%92%8C%E8%B0%81%E9%85%8D%E5%AF%B9%E5%91%A2/%E5%92%8C%E8%B0%81%E9%85%8D%E5%AF%B9%E5%91%A2.m4a"
    print(get_cdn_url(key))