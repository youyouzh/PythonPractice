#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import json
from bs4 import BeautifulSoup

import u_base.u_log as log
import u_base.u_file as u_file

CONFIG = {
    'crawl_max_count': 10,
    'host': 'http://www.posemaniacs.com',
    'page_url_template': '/page/%d',
}


# 提取
def extract_pose_urls(html_content):
    if not html_content:
        log.info('The html content is not valid.')
        return False
    soup = BeautifulSoup(html_content, 'lxml')
    content_node = soup.find(id='content')
    if not content_node:
        log.warn('The content node is not valid.')
        return False
    pose_img_nodes = content_node.select('div.block1 > ul.list > li > a > img')
    pose_urls = []
    for pose_img_node in pose_img_nodes:
        pose_url = pose_img_node['src']
        if pose_url and pose_url != '':
            pose_url = pose_url.replace('_thumb', '')
            pose_url = CONFIG.get('host') + pose_url
            pose_urls.append(pose_url)
    log.info('extract pos urls success. size: {}'.format(len(pose_urls)))
    return pose_urls


def through_pose(url):
    log.info('begin through url'.format(url))
    url_template = url.replace('pose_0001', 'pose_%04d')
    path = os.path.abspath(r'./result')
    if not os.path.isdir(path):
        os.mkdir(path)
    for index in range(1, 50):
        pose_url = url_template % index
        name = re.sub(r"[\\/?*<>|\":]+", '-', pose_url.replace(r'http://www.posemaniacs.com/pose/', ''))
        log.info('begin download image from url: {}'.format(pose_url))
        download_status = u_file.download_image(pose_url, name=name, path=path)
        if not download_status:
            log.info('download end. index: {}'.format(index))
            break


def crawler():
    log.info('------begin crawler------')
    crawl_count = 1
    begin_url = CONFIG.get('host') + (CONFIG.get("page_url_template") % crawl_count)
    html_content = u_file.get_content(begin_url)
    while html_content and crawl_count <= CONFIG.get('crawl_max_count'):
        pose_image_urls = extract_pose_urls(html_content)
        log.info("extract pose image urls success. size: {}".format(len(pose_image_urls)))
        for pose_image_url in pose_image_urls:
            log.info("begin crawl from pose image url: {}".format(pose_image_url))
            through_pose(pose_image_url)
            log.info("end crawl from pose image url: {}".format(pose_image_url))
        crawl_count += 1
        html_content = u_file.get_content(CONFIG.get("page_url_template") % crawl_count)
    log.info('------end crawler------')


if __name__ == '__main__':
    crawler()
