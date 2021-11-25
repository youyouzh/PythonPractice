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
_REQUESTS_KWARGS = {
    'proxies': {
      'https': 'http://127.0.0.1:1080',
    },
}


def extract_boards() -> list:
    """
    获取pinterest用户的图板列表
    :return: list
    """
    return ["人体", "人形", "几何石膏", "动漫-和服", "动漫-萝莉", "古装", "可爱", "技法", "技法-头发", "技法-头部-眼睛-头发",
            "技法-头饰-饰品", "技法-裙子", "材质", "构图", "洛丽塔-2", "洛丽塔-插画图鉴", "特效", "脸型", "色卡", "萝莉塔",
            "蓝色", "静物素描"]


def extract_pins(page_url: str) -> list:
    """
    从页面中提取所有的pin图信息
    :param page_url: 页面url
    :return: pin info list
    """
    log.info('begin request page: {}'.format(page_url))
    html_content = u_file.get_content_with_cache(page_url, **_REQUESTS_KWARGS)

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
    log.info('extract pins success. size: {}'.format(len(pin_infos)))
    return pin_infos


def download_pins(pins: list, board_name: str):
    log.info('begin download board: {} pins image, size: {}'.format(board_name, len(pins)))
    save_dir = r'result'
    save_dir = os.path.join(save_dir, board_name)
    for pin in pins:
        u_file.download_file(pin['image_url'], pin['id'], path=save_dir, **_REQUESTS_KWARGS)
    log.info('end download board: {} pins image, size: {}'.format(board_name, len(pins)))


if __name__ == '__main__':
    for board in extract_boards():
        pins = extract_pins('https://www.pinterest.com/zhyouyui/{}/'.format(board))
        download_pins(pins, board)
