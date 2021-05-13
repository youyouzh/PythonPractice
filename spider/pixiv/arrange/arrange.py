#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os

import pandas as pd

import u_base.u_log as log
from spider.pixiv.arrange.file_util import get_illust_id, get_all_image_paths, get_cache_path
from spider.pixiv.mysql.db import session, Illustration

pd.set_option('max_colwidth', 200)  # 设置打印数据宽度


# 整理所有图片，提取所有图片基本信息
def get_image_meta_infos(target_directory: str, use_cache=True) -> list:
    cache_file_path = get_cache_path(target_directory, 'meta-info', 'json')
    cache_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cache_file_path)
    if use_cache and os.path.isfile(cache_file_path):
        return json.load(open(cache_file_path, 'r', encoding='utf-8'))
    image_meta_infos = []

    image_paths = get_all_image_paths(target_directory, use_cache)
    log.info('total image file size: {}'.format(len(image_paths)))
    index = 0
    for image_path in image_paths:
        index += 1
        illust_id = get_illust_id(image_path)
        # log.info('get illust_id: {} ({}/{})'.format(illust_id, index, len(image_paths)))

        if illust_id < 0:
            log.warn('The illust is not format. image_path: {}'.format(image_path))
            continue

        if not os.path.isfile(image_path):
            log.warn('The illust was deleted. image_path: {}'.format(image_path))
            continue

        illustration: Illustration = session.query(Illustration).get(illust_id)
        if illustration is None:
            log.warn('The illustration is not exist. illust_id: {}'.format(illust_id))
            continue

        image_meta_infos.append({
            'width': illustration.width,
            'height': illustration.height,
            'path': image_path,
            'file_name': os.path.split(image_path)[1],
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


# 检查某个文件夹下的小图片，并把它们移动到该文件夹下的small文件夹下面
def move_small_file(target_directory: str, min_width=800, min_height=800, min_size=10000,
                    use_cache=True, move_directory=None):
    # 如果未指定移动小文件的目标文件夹，则在当前文件夹下生存一个small的子文件夹
    if move_directory is None:
        move_directory = os.path.join(target_directory, 'small')
        if not os.path.isdir(move_directory):
            os.makedirs(move_directory)

    image_meta_infos = get_image_meta_infos(target_directory, use_cache)
    log.info('total image file size: {}'.format(len(image_meta_infos)))

    for image_meta_info in image_meta_infos:
        if not os.path.isfile(image_meta_info.get('path')):
            log.warn('The file is deleted. path: {}'.format(image_meta_info.get('path')))
            continue
        move_target_path = os.path.join(move_directory, image_meta_info.get('file_name'))
        if os.path.isfile(move_target_path):
            log.warn('The move file is exist: {}'.format(move_target_path))

        if image_meta_info.get('size') <= min_size:
            log.info('The file is small. size: ({}/{})'.format(image_meta_info.get('size'), min_size))
            log.info('begin move file from: {} to : {}'.format(image_meta_info.get('path'), move_target_path))
            os.replace(image_meta_info.get('path'), move_target_path)

        if image_meta_info.get('width') <= min_width and image_meta_info.get('height') <= min_height:
            log.info('The file is small, width: ({}/{}), height: ({}/{})'
                     .format(image_meta_info.get('width'), min_width, image_meta_info.get('height'), min_height))
            log.info('begin move file from: {} to : {}'.format(image_meta_info.get('path'), move_target_path))
            os.replace(image_meta_info.get('path'), move_target_path)
    log.info('end move small file')


def check_user_id(source_dir: str, user_dir: str, user_id=None, keep_source=True, use_cache=True, replace_user_file=False):
    """
    检查和移动某个用户下的图片到目标文件夹
    :param user_id: 指定用户id
    :param source_dir: 需要处理的文件夹
    :param user_dir: 某个用户专有的插画集文件夹，移动文件的目标文件夹
    :param keep_source: 是否保留原来的文件，如果存在重复的时候生效
    :param use_cache: 是否使用缓存中的文件目录
    :param replace_user_file: 是否替换掉用户文件夹中的文件
    :return:
    """
    if not os.path.isdir(user_dir):
        log.error('The user directory is not exist. directory: {}'.format(user_dir))
        return None

    parse_user_id = get_illust_id(user_dir)
    if user_id is None and parse_user_id >= 0:
        user_id = parse_user_id

    image_meta_infos = get_image_meta_infos(source_dir, use_cache)
    log.info('total image file size: {}'.format(len(image_meta_infos)))

    index = 0
    move_file_size = 0
    for image_meta_info in image_meta_infos:
        index += 1
        # if index % 1000 == 0:
        #     log.info('processed file size: {}'.format(index))
        if image_meta_info.get('user_id') != user_id:
            continue

        if not os.path.isfile(image_meta_info.get('path')):
            log.info('The file was delete. path: {}'.format(image_meta_info.get('path')))
            continue

        log.info('The illust({}) is belong user_id({}).'.format(image_meta_info.get('illust_id'), user_id))
        move_target_path = os.path.join(user_dir, image_meta_info.get('file_name'))
        if os.path.isfile(move_target_path):
            log.warn('The target user illust is exist: {}, keep: {}'.format(move_target_path, keep_source))
            if keep_source:
                continue

        move_file_size += 1
        if replace_user_file:
            log.info('begin move file from: {} to : {}'.format(image_meta_info.get('path'), move_target_path))
            os.replace(image_meta_info.get('path'), move_target_path)
    log.info('end check user_id, hit file size: {}, dir: {}'.format(move_file_size, user_dir))


def check_repeat():
    target_directory = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'
    image_meta_infos = get_image_meta_infos(target_directory)
    log.info('total image meta infos size: {}'.format(len(image_meta_infos)))
    data_frame = pd.DataFrame(image_meta_infos)

    # 去重
    group_by_illust_id = data_frame.groupby('illust_id')
    log.info('file size: {}, illust size: {}'.format(len(data_frame), len(group_by_illust_id)))
    for illust_id, groups in group_by_illust_id:
        if len(groups) >= 2:
            log.info('The illust is repeat. illust_id: {}'.format(illust_id))
            log.info('\n{}'.format(groups['path']))


if __name__ == '__main__':
    # illust_id = 60881929
    # user_id = get_user_id_by_illust_id(illust_id)

    # user_id = 935581
    # collect_illusts(str(user_id), is_special_illust_ids, 1000, user_id=user_id, use_cache=False)
    # move_small_file(r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\by-user\3302692',
    #                 use_cache=False, min_width=1800, min_height=1800,
    #                 move_directory=r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\small')
    base_dir = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'
    check_user_paths = os.listdir(os.path.join(base_dir, r'collect-user'))
    for check_user_path in check_user_paths:
        check_user_id(source_dir=os.path.join(base_dir, r'collect-favorite'),
                      user_dir=os.path.join(base_dir, os.path.join('collect-user', check_user_path)),
                      keep_source=False, use_cache=True, replace_user_file=False)
