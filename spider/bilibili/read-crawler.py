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
爬取网址： https://www.bilibili.com/read/cv7368315/
爬取图片并下载
基于HTML页面解析爬取
"""
BASE_HOST = 'http://www.j9p.com'
DOWNLOAD_BASE_URL = 'http://jxz1.j9p.com/pc/'


def download_pictures(url: str, title: str) -> list:
    html_content = u_file.get_content(url, encoding='UTF-8')
    soup = BeautifulSoup(html_content, 'lxml')

    img_elements = soup.select('figure.img-box')
    log.info('get book elements size: {}'.format(len(img_elements)))
    for img_element in img_elements:
        image_url = img_element.find('img')['data-src']
        image_url = 'http:' + re.sub(r"@[^\n]+", '-', image_url)
        u_file.download_file(image_url, title + '-' + u_file.get_file_name_from_url(image_url), r'result')
    return []


def get_all_urls(url: str) -> list:
    html_content = u_file.get_content(url, encoding='UTF-8')
    soup = BeautifulSoup(html_content, 'lxml')

    infos = []
    comment_node = soup.select('div.is-top p.text')
    texts = comment_node[0].string.split('\n')
    a_nodes = comment_node[0].find('img')

    index = 1
    for a_node in a_nodes:
        infos.append({
            'url': a_node.href,
            'title': texts[index]
        })
        index += 1
    return infos


if __name__ == '__main__':
    infos = u_file.load_json_from_file(r'result\source.json')
    for info in infos:
        download_pictures(info['url'], u_file.convert_windows_path(info['title']))
