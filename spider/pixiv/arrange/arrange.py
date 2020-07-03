#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

import PIL
import pandas as pd

import u_base.u_log as log
from spider.pixiv.arrange.collect import is_small_size
from spider.pixiv.arrange.file_util import get_illust_id, get_all_image_paths
from spider.pixiv.mysql.db import session, Illustration

pd.set_option('max_colwidth', 200) # 设置打印数据宽度


# 获取某个图片的用户id
def get_user_id_by_illust_id(illust_id: int) -> int:
    illust: Illustration = session.query(Illustration).get(illust_id)
    if not illust:
        log.warn('The illust is not exist. illust_id: {}'.format(illust_id))
        return 0
    return illust.user_id


# 检查和移动某个用户下的图片到目标文件夹
def check_user_id(directory: str):
    if not os.path.isdir(directory):
        log.error('The directory is not exist. directory: {}'.format(directory))
        return None
    illust_files = os.listdir(directory)
    illustrations = []
    user_id_illust_count = {}
    for illust_file in illust_files:
        illust_file_path = os.path.join(directory, illust_file)
        illust_id = get_illust_id(illust_file_path)
        if illust_id <= 0:
            log.warn('The illust id is not exist. illust file: {}'.format(illust_file_path))
            continue
        illustration: Illustration = session.query(Illustration).get(illust_id)
        if illustration is None:
            log.warn('The illustration is not exist. illust_id: {}'.format(illust_id))
            continue
        illustrations.append({
            'id': illustration.id,
            'user_id': illustration.user_id,
            'path': illust_file_path
        })
        log.info('user_id: {}, current path: {}'.format(illustration.user_id, illust_file))
        source_illust_file_path = os.path.abspath(illust_file_path)
        move_target_file_path = os.path.join(os.path.dirname(source_illust_file_path), str(illustration.user_id))
        if not os.path.isdir(move_target_file_path):
            os.makedirs(move_target_file_path)
        move_target_file_path = os.path.join(move_target_file_path, illust_file)
        os.replace(source_illust_file_path, move_target_file_path)
    log.info('check end. size: {}'.format(len(illustrations)))


# 检查和移动小图片
def move_small_file(target_directory: str):
    move_directory = os.path.join(target_directory, 'small-3')
    if not os.path.isdir(move_directory):
        os.makedirs(move_directory)

    # image_paths = get_all_image_paths(target_directory, False)
    image_paths = get_all_image_paths(target_directory)
    log.info('total image file size: {}'.format(len(image_paths)))
    index = 0
    for image_path in image_paths:
        index += 1
        log.info('process image path: {}'.format(image_path))
        if os.path.isfile(image_path):
            move_target_path = os.path.join(move_directory, os.path.split(image_path)[1])
            if os.path.isfile(move_target_path):
                log.warn('The file is exist. can not move: {}'.format(image_path))
                # move_target_path = os.path.join(move_directory, 'index' + '--' + os.path.split(image_path)[1])
                # continue
            try:
                if is_small_size(image_path):
                    log.info('move file from: {} ---> to: {}'.format(image_path, move_target_path))
                    os.replace(image_path, move_target_path)
                    # os.remove(image_path)
            except (PermissionError, PIL.UnidentifiedImageError, FileNotFoundError):
                log.error('PermissionError, file: {}'.format(image_path))


# 整理所有图片，提取所有图片基本信息
def get_image_meta_infos(target_directory: str):
    image_paths = get_all_image_paths(target_directory)
    log.info('total image file size: {}'.format(len(image_paths)))

    cache_file_path = r'cache\image-meta-infos.json'
    cache_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cache_file_path)
    if os.path.isfile(cache_file_path):
        return json.load(open(cache_file_path, 'r', encoding='utf-8'))
    image_meta_infos = []

    index = 0
    for image_path in image_paths:
        index += 1
        illust_id = get_illust_id(image_path)
        log.info('get illust_id: {} ({}/{})'.format(illust_id, index, len(image_paths)))

        if illust_id < 0 or not os.path.isfile(image_path):
            log.warn('The illust is not format. image_path: {}'.format(image_path))
            continue

        illustration: Illustration = session.query(Illustration).get(illust_id)
        if illustration is None:
            log.warn('The illustration is not exist. illust_id: {}'.format(illust_id))
            continue
        image_meta_infos.append({
            'width': illustration.width,
            'height': illustration.height,
            'path': image_path,
            'illust_id': illust_id,
            'user_id': illustration.user_id,
            'size': os.path.getsize(image_path),
            'r_18': illustration.r_18,
            'bookmarks': illustration.total_bookmarks,
            'tag': illustration.tag
        })
    log.info('get_image_meta_infos end. image size: {}'.format(len(image_meta_infos)))
    json.dump(image_meta_infos, open(cache_file_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return image_meta_infos


if __name__ == '__main__':
    # illust_id = 60881929
    # user_id = get_user_id_by_illust_id(illust_id)

    # user_id = 935581
    # collect_illusts(str(user_id), is_special_illust_ids, 1000, user_id=user_id, use_cache=False)
    # target_directory = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\ignore'
    target_directory = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'
    image_meta_infos = get_image_meta_infos(target_directory)
    log.info('total image meta infos size: {}'.format(len(image_meta_infos)))
    data_frame = pd.DataFrame(image_meta_infos)

    # 去重
    group_by_illust_id = data_frame.groupby('illust_id')
    log.info('file size: {}, illust size: {}'.format(len(data_frame), len(group_by_illust_id)))
    # for illust_id, groups in group_by_illust_id:
    #     if len(groups) >= 2:
    #         log.info('The illust is repeat. illust_id: {}'.format(illust_id))
    #         log.info('\n{}'.format(groups['path']))
