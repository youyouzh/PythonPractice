#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
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


def download_image_collect(image_collect: dict, save_dir=r'result'):
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
        u_file.download_file(current_image_url, filename, save_dir)


def crawl_all_picture():
    base_url = 'http://www.jj20.com/bz/nxxz/list_7_cc_12_1.html'
    save_dir = r'result-high'

    base_url = base_url.replace('_1.html', '_{}.html')
    begin_index = 0
    total_page_count = 6
    for index in range(total_page_count):
        if index <= begin_index:
            continue
        log.info('begin extract image collect. ({}/{})'.format(index, total_page_count))
        image_collect_infos = get_image_list(base_url.format(index))
        log.info('image collect size: '.format(len(image_collect_infos)))
        for image_collect_info in image_collect_infos:
            download_image_collect(image_collect_info, save_dir)


# 将第一涨图片挑选出来，方便批量处理
def copy_first_picture():
    picture_paths = u_file.get_all_sub_files(r'result')
    first_picture_paths = []
    for picture_path in picture_paths:
        if picture_path.find('-1.jpg') >= 0:
            first_picture_paths.append(picture_path)

    log.info('first picture size: {}'.format(len(first_picture_paths)))
    for first_picture_path in first_picture_paths:
        copy_file_path = os.path.join(r'result-copy', os.path.split(first_picture_path)[1])
        log.info('copy file: {}'.format(copy_file_path))
        if os.path.isfile(copy_file_path):
            log.info('The file is exist: {}'.format(copy_file_path))
            continue
        shutil.copy(first_picture_path, copy_file_path)


def delete_file():
    delete_picture_paths = u_file.get_all_sub_files(r'result-delete')
    for delete_picture_path in delete_picture_paths:
        base_filename = os.path.split(delete_picture_path)[1]
        for index in range(30):
            source_filename = base_filename.replace('-1', '-' + str(index))
            source_path = os.path.join(r'result', source_filename)
            if not os.path.isfile(source_path):
                break
            log.info('move file: {}'.format(source_path))
            # os.replace(source_path, os.path.join(r'result-other', source_filename))


if __name__ == '__main__':
    crawl_all_picture()
