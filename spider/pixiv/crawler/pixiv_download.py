#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from spider.pixiv.pixiv_api import AppPixivAPI, PixivAPI
from spider.pixiv.mysql.db import save_illustration

CONFIG = json.load(open('config.json'))
_USERNAME = CONFIG.get('username')
_PASSWORD = CONFIG.get('password')
_TEST_WRITE = False

_REQUESTS_KWARGS = {
  # 'proxies': {
  #   'https': 'http://127.0.0.1:1087',
  # },
  # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}
pixiv_api = AppPixivAPI()


# 下载用户收藏列表的图片
def download_user_bookmarks_illusts(user_id):
    if not user_id:
        print('please input the user_id')
        return False
    directory = 'result\\images\\' + str(user_id)
    next_url = True
    page_size = 1
    page_max_size = 20
    while next_url and page_size < page_max_size:
        print('page: %d', page_size)
        json_result = pixiv_api.user_bookmarks_illust(user_id)
        if not json_result:
            break
        for illust in json_result['illusts']:
            image_url = illust.meta_single_page.get('original_image_url', illust.image_urls.large)
            print("%d: %s: %s" % (illust.id, illust.title, image_url))
            url_basename = os.path.basename(image_url)
            extension = os.path.splitext(url_basename)[1]
            name = "illust_%d_%s%s" % (illust.id, illust.user.id, extension)
            pixiv_api.download(image_url, path=directory, name=name)
        page_size += 1
        next_url = str(json_result.next_url)


def download_user_illusts(user_id):
    if not user_id:
        print('please input the user_id')
        return False
    directory = 'result\\images\\' + str(user_id)
    next_url = '-'
    page_size = 1
    page_max_size = 20
    while next_url and page_size < page_max_size:
        print('page: %d', page_size)
        json_result = pixiv_api.user_illusts(user_id)
        if not json_result:
            break
        for illust in json_result['illusts']:
            image_url = illust.meta_single_page.get('original_image_url', illust.image_urls.large)
            print("%d: %s: %s" % (illust.id, illust.title, image_url))
            url_basename = os.path.basename(image_url)
            extension = os.path.splitext(url_basename)[1]
            name = "illust_%d_%s%s" % (illust.id, illust.user.id, extension)
            pixiv_api.download(image_url, path=directory, name=name)
        page_size += 1
        next_url = str(json_result.next_url)


def rank_of_day():
    json_result = pixiv_api.illust_ranking('day_male')
    print(json_result)
    illust = json_result.illusts[0]
    print(">>> %s, origin url: %s" % (illust.title, illust.image_urls['large']))

    directory = r"result/rank_of_day/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    pixiv_api.download(illust.image_urls['large'], '', directory, replace=True)

    # get next page
    # next_qs = pixiv_api.parse_qs(json_result.next_url)
    # json_result = pixiv_api.illust_ranking(**next_qs)
    # # print(json_result)
    # illust = json_result.illusts[0]
    # print(">>> %s, origin url: %s" % (illust.title, illust.image_urls['large']))


if __name__ == '__main__':
    pixiv_api.login(_USERNAME, _PASSWORD)
    illusts = pixiv_api.illust_ranking('day_male')
    for illust in illusts.get('illusts'):
        save_illustration(illust)

