#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from spider.pixiv.pixiv_api import AppPixivAPI, PixivAPI

CONFIG = json.load(open('config.json'))
_USERNAME = CONFIG.get('username')
_PASSWORD = CONFIG.get('password')
_TEST_WRITE = False

## If a special network environment is meet, please configure requests as you need.
## Otherwise, just keep it empty.
_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'https': 'http://127.0.0.1:1087',
    # },
    # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}


def to_json_str(response):
    return json.dumps(response, ensure_ascii=False, indent=4)


def main():
    # app-api
    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.login(_USERNAME, _PASSWORD)
    # response = pixiv_api.user_detail(illust_detail)
    # response = pixiv_api.illust_detail(68376038)
    # response = pixiv_api.illust_detail(75987864)  # R-18
    response = pixiv_api.illust_ranking('day')
    print(to_json_str(response))


if __name__ == '__main__':
    main()
