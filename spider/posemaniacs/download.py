#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import json
from bs4 import BeautifulSoup

import u_base.u_log as log
import u_base.u_file as u_file


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
            pose_url = 'http://www.posemaniacs.com' + pose_url
            pose_urls.append(pose_url)
    log.info('extract pos urls success. size: {}'.format(len(pose_urls)))
    return pose_urls


def through_pose(url):
    log.info('begin through url'.format(url))
    url_template = url.replace('pose_0001', 'pose_%04d')
    path = os.path.abspath(r'./result')
    if not os.path.isdir(path):
        os.mkdir(path)
    for index in range(1, 20):
        pose_url = url_template % index
        name = re.sub(r"[\\/?*<>|\":]+", '', pose_url.replace(r'http://www.posemaniacs.com/pose/', ''))
        log.info('begin download image from url: {}'.format(pose_url))
        download_status = u_file.download_image(pose_url, name=name)
        if not download_status:
            break


if __name__ == '__main__':
    html_content = u_file.get_content(os.path.abspath('./page/index.html'))
    pose_img_urls = extract_pose_urls(html_content)
    for pose_image_url in pose_img_urls:
        through_pose(pose_image_url)
