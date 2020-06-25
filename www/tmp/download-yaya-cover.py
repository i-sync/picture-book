#!/usr/bin/env python3
# -*- coding: utf-8-*-

import os
import re
import json
import requests

#ROOT_PATH = '/mnt/sda1/xmly-huiben'
ROOT_PATH = '/media/Study/yaya-huiben'


class Downloader:
    @classmethod
    def download_file(cls, url):
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        }

        res = requests.get(url, headers=headers)
        if res.status_code != requests.codes.ok:
            return None
        return res.content

    @classmethod
    def write_file(cls, file_name, file_content):
        if os.path.exists(file_name):
            os.remove(file_name)
        with open(file_name, 'wb') as f:
            f.write(file_content)

def download_album_cover():
    error = []
    for folder_name in os.listdir(ROOT_PATH):
        print(folder_name)
        folder_id = folder_name[:folder_name.find('.')]

        detail_json_name = f"{ROOT_PATH}/{folder_name}/{folder_id}.resourceDetail.json"
        detail_obj = {}
        with open(detail_json_name, 'r', encoding='utf-8') as f:
            detail_obj = json.load(f)
        cover_url = detail_obj['data']['resource']['cover']
        cover_ext = cover_url[cover_url.rfind('.'):]

        cover_file = f"{ROOT_PATH}/{folder_name}/cover{cover_ext}"
        if os.path.exists(cover_file):
            print("EXISTS, SKIP!!!")
            continue

        file_content = Downloader.download_file(cover_url.replace('.png', '_600x600.png'))
        # check if download success
        if file_content is None:
            print(cover_file, "download image failed...")
            error.append(folder_name)
        else:
            Downloader.write_file(cover_file, file_content)

        #break

    if len(error):
        print(error)

if __name__ == '__main__':
    download_album_cover()