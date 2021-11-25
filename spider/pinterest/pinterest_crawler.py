#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import re
import os
from bs4 import BeautifulSoup
import u_base.u_file as u_file
import u_base.u_log as log

# global config
config = {
    'begin_article': 0,      # 开始扫描的文章数，便于继续扫描
    'max_article': 10,       # 扫描的最大文章数
    'console_output': True,  # 是否控制台输出d
    'template_input_html': 'page/template.html',  # 输入HTML路径，控制显示样式
    'output_html_path': 'page/output.html',    # 输出HTML路径，空则不输出
    'output_json_path': 'page/result.json',    # 输出json路径，空则不输出
}
CRAWL_HOST = 'https://www.pinterest.com/'
INIT_JSON_PARSE_PATTERN = re.compile('__PWS_DATA__[^{]+(.+www"})</script>')


def extract_pins(page_url: str) -> list:
    cache_file = r'cache\page.html'
    log.info('begin request page: {}'.format(page_url))
    html_content = u_file.get_cache_content(page_url, cache_file, use_cache=False)

    # 返回结果通过js处理成document，只能正则匹配
    json_data = u_file.extract_init_json_data(html_content, INIT_JSON_PARSE_PATTERN)
    log.info("extract json data success.")
    if u_file.m_get(json_data, 'props.initialReduxState.pins') is None:
        log.error('The pins key is not exist.')
        return []

    pins: {} = u_file.m_get(json_data, 'props.initialReduxState.pins')
    pin_infos = []
    for pin in pins.values():
        pin_infos.append({
            'id': pin['id'],
            'type': pin['type'],
            'dominant_color': pin['dominant_color'],
            'description': pin['description'],
            'domain': pin['domain'],
            'grid_title': pin['grid_title'],
            'image_url': pin['images']['orig']['url'],
            'width': pin['images']['orig']['width'],
            'height': pin['images']['orig']['height'],
            'image_signature': pin['image_signature'],
            'link': pin['link']
        })
    return pin_infos


def download_pins(pins: list):
    log.info('begin download pins image, size: {}'.format(len(pins)))
    save_dir = r'result'
    for pin in pins:
        u_file.download_file(pin['image_url'], pin['id'], save_dir)


if __name__ == '__main__':
    pins = extract_pins('https://www.pinterest.com/zhyouyui/%E6%9D%90%E8%B4%A8/')
    download_pins(pins)
