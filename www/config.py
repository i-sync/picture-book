#!/usr/bin/env python
# _*_ coding: utf-8 _*_

'''
config.py
'''

#import config_default
import os.path
import json
import hashlib

from common import toDict, merge

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')

configs = None
user = None
with open('{}/config.json'.format(path), encoding='utf-8') as f:
    configs = json.load(f)

with open('{}/user.json'.format(path), encoding='utf-8') as f:
    user = json.load(f)

configs = merge(configs, user)

configs = toDict(configs)

usernames = None
with open('{}/username.json'.format(path), encoding='utf-8') as f:
    usernames = json.load(f)
for u in usernames:
    u['hashname'] = hashlib.sha256(u['username'].encode()).hexdigest()
usernames =[toDict(u) for u in usernames]
