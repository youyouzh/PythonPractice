#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from spider.pixiv.pixiv_api import AppPixivAPI, PixivAPI
from spider.pixiv.mysql.db import save_illustration, query_top_total_bookmarks, get_illustration, get_illustration_image

CONFIG = json.load(open('config.json'))
_USERNAME = CONFIG.get('username')
_PASSWORD = CONFIG.get('password')
_TEST_WRITE = False

# If a special network environment is meet, please configure requests as you need.
# Otherwise, just keep it empty.
_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'https': 'http://127.0.0.1:1087',
    # },
    # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}


def to_json_str(response):
    return json.dumps(response, ensure_ascii=False, indent=4)


def save_illust(illust=None):
    if illust is None:
        # illust = json.load(open(r"../mysql/entity_example/illust-multi.json", encoding='utf8'))
        illust = json.load(open(r"../mysql/entity_example/illust.json", encoding='utf8'))
    if 'illust' in illust:
        save_illustration(illust.get('illust'))
        print("save success")
    else:
        print("illust is empty.")


def main():
    # app-api
    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.login(_USERNAME, _PASSWORD)
    # response = pixiv_api.user_detail(illust_detail)
    # response = pixiv_api.illust_detail(68376038)  # single page
    response = pixiv_api.illust_detail(75872584)  # multi page
    # response = pixiv_api.illust_detail(75987864)  # R-18
    # response = pixiv_api.illust_ranking('day')    # ranking
    print(to_json_str(response))
    save_illust(response)


if __name__ == '__main__':
    # main()
    # save_illust()
    result = get_illustration_image(64118130)
    result = get_illustration(64118130)
    print(result)
