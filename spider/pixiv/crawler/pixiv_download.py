#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import threadpool
import re

from spider.pixiv.pixiv_api import AppPixivAPI
from spider.pixiv.mysql.db import save_illustration, get_illustration, get_illustration_image, Illustration,\
    query_top_total_bookmarks, update_illustration_image, get_illustration_tag, IllustrationTag, IllustrationImage, \
    session

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


# 下载指定user_id的所有插画
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


# 按天排行下载
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
    max_page_count = 10
    is_r18 = False
    date_offset_file = 'offset-r-18.json' if is_r18 else 'offset.json'
    date_offset_info = json.load(open(date_offset_file))

    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    query_date = datetime.datetime.strptime(date_offset_info.get('date'), '%Y-%m-%d').date()
    now = datetime.date.today()
    total_query_count = 0
    print('------------begin-------------' + str(datetime.datetime.now()))
    while query_date < now:
        # 依次查询每一天的排行榜
        print('query date: %s, offset: %s' % (str(query_date), str(date_offset_info.get('offset'))))
        page_index = 0
        next_url_options = {
            'mode': 'day_r18' if is_r18 else 'day',
            'date': query_date,
            'offset': date_offset_info.get('offset')
        }
        while page_index < max_page_count:
            # 每天查询 max_page_count 次
            print("----> date: %s, page index: %d, query count: %d" % (str(query_date), page_index, total_query_count))
            illusts = pixiv_api.illust_ranking(**next_url_options)
            # illusts = json.load(open(r"../mysql/entity_example/rank-1.json", encoding='utf8'))
            if not illusts.get('illusts'):
                # 查询结果为空，分两种情况，一种是发生错误，一种是没有数据了
                print('illust is empty.' + str(illusts) + '-------' + str(datetime.datetime.now()))
                if 'error' not in illusts:
                    # 不是发生了错误，那就是这天的数据已经爬完了，接着爬明天的
                    break

                if illusts.get('error').get('message', '').find('Rate Limit') >= 0:
                    # 访问频率限制则等待一下继续重试
                    time.sleep(10)
                if illusts.get('error').get('message', '').find('OAuth') >= 0:
                    # token过期(一个小时就会过期)，刷新token然后重试
                    print("Access Token is invalid, refresh token.")
                    pixiv_api.auth()
                continue

            # 提取下次的爬取连接，并把数据保存
            next_url_options = pixiv_api.parse_next_url_options(illusts.get('next_url'))
            total_query_count += 1
            page_index += 1
            print('next url: ' + illusts.get('next_url'))
            print("----> illust size: ", len(illusts.get('illusts')))
            for illust in illusts.get('illusts'):
                illust['r_18'] = is_r18
                save_illustration(illust)

            # 将爬取的时间和偏移持久化，即使中断下次也可以接着爬
            date_offset_info['date'] = str(query_date)
            date_offset_info['offset'] = next_url_options['offset']
            json.dump(date_offset_info, open(date_offset_file, 'w'), ensure_ascii=False, indent=4)

        # 爬取下一天的数据
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


# 从本地数据查找URL，然后下载图片
def download_by_illustration_id(pixiv_api, directory, illustration_id: int):
    illustration: Illustration = get_illustration(illustration_id)
    if illustration is None:
        print('The illustration is not exist. illustration_id: ' + str(illustration_id))
        return
    illustration_images: [IllustrationImage] = get_illustration_image(illustration_id)
    if illustration_images is None or len(illustration_images) == 0:
        print('The illustration image is not exist. illustration_id: ' + str(illustration_id))
        return
    if len(illustration_images) > 3:
        # 超过3幅的画，大多是漫画类型，先不管
        print('The illustration images are more than 3. illustration_id: ' + str(illustration_id))
        return

    # 按照收藏点赞人数分文件夹
    directory += '/' + '-'.join(str(i) for i in get_10_20(illustration.total_bookmarks))

    if illustration.r_18 is not None and illustration.r_18 == 1:
        # R18放在别的文件夹
        directory += "/r-18"

    for illustration_image in illustration_images:
        if illustration_image.image_url_origin is None or illustration_image.image_url_origin == '':
            print('The illustration_image image_url_origin is none. illustration_id: ' + str(illustration_id))
            continue
        if illustration_image.process == 'DOWNLOADED':
            print('The illustration_image has been downloaded. illustration_id: ' + str(illustration_id))
            continue
        print('begin process illust_id: %s, image_url: %s' % (illustration_image.illust_id,
                                                              illustration_image.image_url_origin))
        download_task(pixiv_api, directory, illustration_image=illustration_image)
        illustration_image.process = 'DOWNLOADED'
        update_illustration_image(illustration_image)


# 下载指定地址的图片
def download_task(pixiv_api, directory, url=None, illustration_image: IllustrationImage = None):
    begin_time = time.time()
    name = None
    if not os.path.exists(directory):
        # 递归创建文件夹
        os.makedirs(directory)
    if url is None or illustration_image is not None:
        # 通过illustration_image下载
        illustration_tags = get_illustration_tag(illustration_image.illust_id)
        url = illustration_image.image_url_origin
        basename = os.path.basename(url).split('.')
        tags = list()
        for illustration_tag in illustration_tags:
            if illustration_tag.name not in tags:
                tags.append(illustration_tag.name)
        # 过滤掉tag名称中的特殊字符，避免无法创建文件
        name = re.sub(r"[\\/?*<>|\":]+", '', '-'.join(tags))[0:150]
        name = str(basename[0]) + '-' + name + '.' + str(basename[1])
    try:
        pixiv_api.download(url, '', directory, replace=False, name=name)
    except (OSError, NameError):
        print("save error, try again.")
        pixiv_api.download(url, '', directory, replace=False, name=name)
    print('download image end. cast: %f, url: %s' % (time.time() - begin_time, url))


# 下载TOP收藏图片
def download_top():
    directory = r"result/illusts"
    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    top_illusts = query_top_total_bookmarks()
    print("illus top size: " + str(len(top_illusts)))
    for top_illust in top_illusts:
        print("begin download illust: " + str(top_illust))
        download_by_illustration_id(pixiv_api, directory, top_illust["id"])


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


# 获取整数倍 2324 -> [2000, 3000]
def get_10_20(number: int):
    figure = 0
    remain = number
    while remain // 10 > 0:
        remain = remain // 10
        figure += 1
    return [remain * (10 ** figure), (remain + 1) * (10 ** figure)]


if __name__ == '__main__':
    # crawl_rank_illust_info()
    # download_by_pool()
    download_top()
