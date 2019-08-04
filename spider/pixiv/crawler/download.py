#!/usr/bin/python
# -*- coding: utf-8 -*

import json
import os
from spider.pixiv.pixiv_api import AppPixivAPI, PixivAPI
from spider.pixiv.mysql.db import save_illustration

CONFIG = json.load(open('config.json'))
_USERNAME = CONFIG.get('username')
_PASSWORD = CONFIG.get('password')


if __name__ == '__main__':
    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    download_url = r'https://i.pximg.net/img-original/img/2017/04/05/00/00/02/62258773_p0.png'
    print('------begin download image------: ' + download_url)
    directory = r"result/images/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    pixiv_api.download(download_url, '', directory, replace=False)
    print('------end download image------')

