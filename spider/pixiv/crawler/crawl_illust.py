#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import threadpool
import re

from spider.pixiv.pixiv_api import AppPixivAPI
from spider.pixiv.mysql.db import save_illustration

CONFIG = json.load(open(r'config\config.json'))
_USERNAME = CONFIG.get('username')
_PASSWORD = CONFIG.get('password')


# 爬取用户收藏列表的图片
def crawl_user_bookmarks_illusts(user_id):
    if not user_id:
        print('please input the user_id')
        return False
    next_url = True
    page_index = 1
    page_max_size = 20
    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    while next_url and page_index < page_max_size:
        print('page: %d', page_index)
        json_result = pixiv_api.user_bookmarks_illust(user_id)
        if not json_result:
            break
        for illust in json_result['illusts']:
            save_illustration(illust)
        page_index += 1
        next_url = str(json_result.next_url)


# 爬取指定user_id的所有插画
def crawl_user_illusts(user_id):
    if not user_id:
        print('please input the user_id')
        return False
    directory = 'result\\images\\' + str(user_id)
    next_url = '-'
    page_index = 1
    page_max_size = 20
    pixiv_api = AppPixivAPI()
    pixiv_api.login(_USERNAME, _PASSWORD)
    while next_url and page_index < page_max_size:
        print('page: %d', page_index)
        json_result = pixiv_api.user_illusts(user_id)
        if not json_result:
            break
        for illust in json_result['illusts']:
            save_illustration(illust)
        page_index += 1
        next_url = str(json_result.next_url)


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


if __name__ == '__main__':
    crawl_rank_illust_info()
