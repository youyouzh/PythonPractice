#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import re
import time
import threadpool
from bs4 import BeautifulSoup

import u_base.u_log as log
import u_base.u_file as u_file


def get_image_list(url: str) -> list:
    html_content = u_file.get_content(url, encoding='gb2312')
    soup = BeautifulSoup(html_content, 'lxml')

    # find image collection
    image_li_elements = soup.select('ul.picbz > li')
    log.info('image li list siz: {}'.format(len(image_li_elements)))

    image_collects = []
    for image_li_element in image_li_elements:
        a_element = image_li_element.findAll('a')
        a_element = a_element[1]
        image_collects.append({
            'url': 'http://www.jj20.com' + a_element['href'],
            'title': a_element.string
        })
    return image_collects


def download_image_collect(image_collect: dict):
    html_content = u_file.get_content(image_collect['url'], encoding='gb2312')
    soup = BeautifulSoup(html_content, 'lxml')

    image_collection_img_elements = soup.select('ul#showImg > li img')
    image_count = len(image_collection_img_elements)
    log.info('The image collect image size: {}'.format(image_count))

    # image_download_button_element = soup.select('span#kk > a')
    # full_image_url = image_download_button_element['href']
    # full_image_url = full_image_url.replace('http://cj.jj20.com/2020/down.html?picurl=', 'http://pic.jj20.com')
    for image_collection_img_element in image_collection_img_elements:
        current_image_url = image_collection_img_element['src']
        current_image_url = current_image_url.replace('-lp', '')
        filename = image_collect['title'] + '-' + u_file.get_file_name_from_url(current_image_url)
        u_file.download_file(current_image_url, filename, r'result')


if __name__ == '__main__':
    base_url = 'http://www.jj20.com/bz/nxxz/list_7_cc_13_{}.html'
    total_page_count = 133
    for index in range(total_page_count):
        if index <= 78:
            continue
        log.info('begin extract image collect. ({}/{})'.format(index, total_page_count))
        image_collect_infos = get_image_list(base_url.format(index))
        log.info('image collect size: '.format(len(image_collect_infos)))
        for image_collect_info in image_collect_infos:
            download_image_collect(image_collect_info)
