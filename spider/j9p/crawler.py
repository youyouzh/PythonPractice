#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import shutil
import re
import json
from bs4 import BeautifulSoup

import u_base.u_log as log
import u_base.u_file as u_file

"""
爬取网址： http://www.j9p.com/class/188_7.html
爬取图书地址等信息，然后批量下载
基于HTML页面解析爬取
"""
BASE_HOST = 'http://www.j9p.com'
DOWNLOAD_BASE_URL = 'http://jxz1.j9p.com/pc/'


def get_book_list(url: str) -> list:
    html_content = u_file.get_content(url, encoding='gb2312')
    soup = BeautifulSoup(html_content, 'lxml')

    book_elements = soup.select('li.item > a')
    log.info('get book elements size: {}'.format(len(book_elements)))

    book_infos = []
    for book_element in book_elements:
        book_infos.append({
            'download_page': BASE_HOST + book_element['href'],
            'cover_image_url': book_element.find('img', {'class': 'tu'})['src'],
            'title': book_element.select('div.info > p.name')[0].string,
            'update_time': book_element.select('div.info > p.type > span')[0].string,
            'size': book_element.select('div.info > p.type > span')[1].string
        })
    u_file.cache_json(book_infos, r'result/book_info.json')
    return book_infos


def get_all_page_book_list(template_url: str) -> list:
    max_page_size = 100
    book_infos = []
    for index in range(1, max_page_size):
        url = template_url.format(index)
        page_book_infos = get_book_list(url)
        if len(page_book_infos) == 0:
            log.warn('The book infos is empty. end crawler.')
            break
        book_infos.extend(page_book_infos)
        log.info('end crawler url: {}, book size: {}'.format(url, len(page_book_infos)))
        u_file.cache_json(book_infos, r'result/total_book_info.json')
    return book_infos


def fill_download_url(book_infos: list) -> list:
    log.info('total book infos size: {}'.format(len(book_infos)))
    for book_info in book_infos:
        if 'download_url' in book_info:
            log.info('This books has filled download_url. {}'.format(book_info))
            continue
        html_content = u_file.get_content(book_info['download_page'], encoding='gb2312')

        # 返回结果通过js处理成document
        download_info_pattern = re.compile(r'_downInfo = (\{Address:.+\})</script>')
        address_pattern = re.compile(r'_downInfo = \{Address:\"(.+)\",TypeID')

        search_download_content = re.search(download_info_pattern, html_content)
        search_address_content = re.search(address_pattern, html_content)
        if search_address_content is None:
            log.error('Can not match any data.')
            continue

        download_address = search_address_content.group(1)
        log.info('download_info: {}'.format(search_download_content.group(1)))

        book_info['download_url'] = DOWNLOAD_BASE_URL + download_address
        book_info['download_info'] = search_download_content.group(1)
        u_file.cache_json(book_infos, r'result/full_book_infos.json')
    return book_infos


if __name__ == '__main__':
    book_infos = u_file.load_json_from_file(r'result/full_book_infos.json')
    book_infos.sort(key=lambda x: x['title'])
    u_file.cache_json(book_infos, r'result/sort_book_infos.json')
