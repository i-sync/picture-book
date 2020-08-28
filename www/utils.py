#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import re
import string
import hashlib
import random
import urllib.parse


def fixed_file_name(file_name: str):
    file_name = re.sub(r'\s', '-', file_name)
    file_name = re.sub(r'[^\w\-_\. ]', '-', file_name)
    file_name = re.sub(r'-{2,}', '-', file_name)
    return file_name.strip('-')


def get_cdn_url(cls, path):
    '''
    Get cdn url
    :param cls:
    :param path:
    :return:
    '''
    timestamp = round(time.time())
    rand = ''.join(random.sample(string.ascii_letters + string.digits, random.randint(20, 30)))
    uid = 0
    md5hash = hashlib.md5(f"/{urllib.parse.quote(path)}-{timestamp}-{rand}-{uid}-{configs.cdn.secret}".encode('utf-8')).hexdigest()
    return f"https://cdn.picture.viagle.com/{urllib.parse.quote(path)}?sign={timestamp}-{rand}-{uid}-{md5hash}"