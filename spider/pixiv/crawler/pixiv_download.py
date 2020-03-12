#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import threadpool
from spider.pixiv.pixiv_api import AppPixivAPI
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


# 下载用户收藏列表的图片
def download_user_bookmarks_illusts(user_id):
    if not user_id:
        print('please input the user_id')
        return False
    directory = 'result\\images\\' + str(user_id)
    next_url = True
    page_size = 1
    page_max_size = 20
    pixiv_api = AppPixivAPI()
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
    pixiv_api = AppPixivAPI()
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
    pixiv_api = AppPixivAPI()
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


# 爬取所有每日榜单并保存
def crawl_rank_illust_info():
    max_page_count = 50
    # 将爬取的时间和偏移持久化，下次可以接着爬
    date_offset_file = 'offset.json'
    is_r18 = False
    date_offset_info = json.load(open(date_offset_file))

    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    query_date = datetime.datetime.strptime(date_offset_info.get('date'), '%Y-%m-%d').date()
    now = datetime.date.today()
    total_query_count = 0
    print('------------begin-------------' + str(datetime.datetime.now()))
    while query_date < now:
        print('query date: %s, offset: %s' % (str(query_date), str(date_offset_info.get('offset'))))
        page_index = 0
        next_url_options = {
            'mode': 'day_r18' if is_r18 else 'day',  # day_r18
            'date': query_date,
            'offset': date_offset_info.get('offset-r-18.json' if is_r18 else 'offset.json')
        }
        time.sleep(2)
        while page_index < max_page_count:
            print("----> date: %s, page index: %d, query count: %d" % (str(query_date), page_index, total_query_count))
            illusts = pixiv_api.illust_ranking(**next_url_options)
            # illusts = json.load(open(r"../mysql/entity_example/rank-1.json", encoding='utf8'))
            if not illusts.get('illusts'):
                print('illust is empty.' + str(illusts) + '-------' + str(datetime.datetime.now()))
                break
            next_url_options = pixiv_api.parse_next_url_options(illusts.get('next_url'))
            total_query_count += 1
            page_index += 1
            print('next url: ' + illusts.get('next_url'))
            print("----> illust size: ", len(illusts.get('illusts')))
            for illust in illusts.get('illusts'):
                illust['r_18'] = is_r18
                save_illustration(illust)
            date_offset_info['date'] = str(query_date)
            date_offset_info['offset'] = next_url_options['offset']
            json.dump(date_offset_info, open(date_offset_file, 'w'), ensure_ascii=False, indent=4)
        query_date = query_date + datetime.timedelta(days=1)
        date_offset_info['offset'] = 0
    print('-------------end-----------')


# 从文件中获取下载链接
def get_download_url_from_file():
    # 读取需要下载的URL
    url_list = []
    download_urls_file = 'download_urls.txt'
    file_handler = open(download_urls_file)
    line = file_handler.readline()
    while line:
        line = line.strip('\n')
        if line and line != '':
            url_list.append(line)
        line = file_handler.readline()
    return url_list


# 下载指定地址的图片
def download_task(pixiv_api, directory, url):
    print('download image begin: %s, url: %s' % (time.time(), url))
    pixiv_api.download(url, '', directory, replace=False)
    print('download image end: %s, url: %s' % (time.time(), url))


def download():
    # 创建文件夹
    directory = r"result/images/35-40/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    url_list = get_download_url_from_file()
    print('begin download image, url size: ' + str(len(url_list)))
    index = 0
    for url in url_list:
        print('index: ' + str(index))
        download_task(pixiv_api, directory, url)
        index += 1


def download_by_pool():
    # 创建文件夹
    directory = r"result/images/2012-2016-1000-1500/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    url_list = get_download_url_from_file()
    print('begin download image, url size: ' + str(len(url_list)))
    pool = threadpool.ThreadPool(8)
    params = map(lambda v: (None, {'pixiv_api': pixiv_api, 'directory': directory, 'url': v}), url_list)
    task_list = threadpool.makeRequests(download_task, params)
    [pool.putRequest(task) for task in task_list]
    pool.wait()


if __name__ == '__main__':
    crawl_rank_illust_info()
    # download_by_pool()



