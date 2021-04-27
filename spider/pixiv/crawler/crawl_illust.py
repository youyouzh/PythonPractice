#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import datetime
import time
import threadpool
import re

import u_base.u_log as log
from spider.pixiv.pixiv_api import AppPixivAPI
from spider.pixiv.mysql.db import save_illustration


CONFIG = json.load(open(r'config\config.json', encoding='utf-8'))
_USERNAME = CONFIG.get('username')
_PASSWORD = CONFIG.get('password')
_REFRESH_TOKEN = CONFIG.get('token')
_REQUESTS_KWARGS = {
    'proxies': {
      'https': 'http://127.0.0.1:1080',
    },
    # 'verify': False,       # PAPI use https, an easy way is disable requests SSL verify
}


# 爬取用户收藏列表的图片
def crawl_user_bookmarks_illusts(user_id):
    if not user_id:
        log.error('please input the user_id.')
        return False
    next_url = True
    page_index = 1
    page_max_size = 20
    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.login(_USERNAME, _PASSWORD)
    while next_url and page_index < page_max_size:
        log.info('page index: {}'.format(page_index))
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
        log.error('please input the user_id.')
        return False
    directory = 'result\\images\\' + str(user_id)
    next_url = '-'
    page_index = 1
    page_max_size = 20
    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.auth(refresh_token=_REFRESH_TOKEN)
    while next_url and page_index < page_max_size:
        log.info('page index: {}'.format(page_index))
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
    date_offset_file = r'.\config\offset-r-18.json' if is_r18 else r'.\config\offset.json'
    date_offset_info = json.load(open(date_offset_file, encoding='utf-8'))
    log.info('init date_offset_info success. {}'.format(date_offset_info))

    pixiv_api = AppPixivAPI(**_REQUESTS_KWARGS)
    pixiv_api.auth(refresh_token=_REFRESH_TOKEN)
    query_date = datetime.datetime.strptime(date_offset_info.get('date'), '%Y-%m-%d').date()
    now = datetime.date.today()
    total_query_count = 0
    sleep_second = 10   # 触发频率限制的等待时间
    log.info('------------begin crawler-------------')
    while query_date < now:
        # 依次查询每一天的排行榜
        page_index = 0
        next_url_options = {
            'mode': 'day_r18' if is_r18 else 'day',
            'date': query_date,
            'offset': date_offset_info.get('offset')
        }
        log.info('begin crawl date: {}, offset: {}'.format(query_date, date_offset_info.get('offset')))
        while page_index < max_page_count:
            # 每天查询 max_page_count 次
            log.info('begin crawl illust info({}/{}). options: {}'.format(page_index, max_page_count, next_url_options))
            illusts = pixiv_api.illust_ranking(**next_url_options)
            log.info('end crawl illust info({}/{}). options: {}'.format(page_index, max_page_count, next_url_options))
            # illusts = json.load(open(r"../mysql/entity_example/rank-1.json", encoding='utf8'))
            if not illusts.get('illusts'):
                # 查询结果为空，分两种情况，一种是发生错误，一种是没有数据了
                log.warn('The response illusts is empty: {}'.format(illusts))
                if 'error' not in illusts:
                    # 不是发生了错误，那就是这天的数据已经爬完了，接着爬明天的
                    log.info('The response is not error. It means today illusts are crawled finish.')
                    break

                if illusts.get('error').get('message', '').find('Rate Limit') >= 0:
                    # 访问频率限制则等待一下继续重试
                    log.warn('Touch Rate Limit. sleep {} second.'.format(sleep_second))
                    time.sleep(sleep_second)
                if illusts.get('error').get('message', '').find('OAuth') >= 0:
                    # token过期(一个小时就会过期)，刷新token然后重试
                    log.warn("Access Token is invalid, refresh token.")
                    pixiv_api.auth()
                continue

            # 提取下次的爬取连接，并把数据保存
            log.info('extract next url: {}'.format(illusts.get('next_url')))
            next_url_options = pixiv_api.parse_next_url_options(illusts.get('next_url'))
            total_query_count += 1
            page_index += 1
            log.info("crawl success. illust size: {}, begin save info to db.".format(len(illusts.get('illusts'))))
            for illust in illusts.get('illusts'):
                illust['r_18'] = is_r18
                save_illustration(illust)

            log.info('crawl illust save database success. illust size: {}'.format(len(illusts.get('illusts'))))
            # 将爬取的时间和偏移持久化，即使中断下次也可以接着爬
            date_offset_info['date'] = str(query_date)
            date_offset_info['offset'] = next_url_options['offset']
            json.dump(date_offset_info, open(date_offset_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

        # 爬取下一天的数据
        query_date = query_date + datetime.timedelta(days=1)
        date_offset_info['offset'] = 0
    log.info('------------end crawler-------------')
    log.info('total query count: {}'.format(total_query_count))


if __name__ == '__main__':
    crawl_rank_illust_info()
