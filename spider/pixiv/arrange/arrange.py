#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

import pandas as pd

import u_base.u_file as u_file
from u_base.u_log import logger as log
from spider.pixiv.arrange.file_util import get_illust_id, get_cache_path
from spider.pixiv.mysql.db import Illustration, query_by_user_id, get_illustration_by_id, is_download_user


def get_path_illust_meta_infos(target_directory: str, use_cache=True) -> list:
    """
    获取目标文件夹下的所有插画元数据信息
    :param target_directory: 目标文件夹
    :param use_cache: 是否使用缓存
    :return: 图片元数据信息
    """
    cache_file_path = get_cache_path(target_directory, 'illust-info', 'json')
    cache_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cache_file_path)
    if use_cache and os.path.isfile(cache_file_path):
        return u_file.load_json_from_file(cache_file_path)
    image_meta_infos = []

    illust_paths = u_file.get_all_sub_files_with_cache(target_directory, use_cache=use_cache)
    log.info('total image file size: {}'.format(len(illust_paths)))
    index = 0
    for illust_path in illust_paths:
        index += 1
        illust_id = get_illust_id(illust_path)
        # log.info('get illust_id: {} ({}/{})'.format(illust_id, index, len(image_paths)))

        if illust_id < 0:
            log.warn('The illust is not format. image_path: {}'.format(illust_path))
            continue

        if not os.path.isfile(illust_path):
            log.warn('The illust was deleted. image_path: {}'.format(illust_path))
            continue

        illustration: Illustration = get_illustration_by_id(illust_id)
        if illustration is None:
            log.warn('The illustration is not exist. illust_id: {}'.format(illust_id))
            continue

        image_meta_infos.append({
            'width': illustration.width,
            'height': illustration.height,
            'path': illust_path,
            'file_name': os.path.split(illust_path)[1],
            'illust_id': illust_id,
            'user_id': illustration.user_id,
            'size': os.path.getsize(illust_path),
            'r_18': illustration.r_18,
            'bookmarks': illustration.total_bookmarks,
            'tag': illustration.tag
        })
    log.info('get_image_meta_infos end. image size: {}'.format(len(image_meta_infos)))
    u_file.dump_json_to_file(cache_file_path, image_meta_infos)
    return image_meta_infos


def move_small_file(source_dir: str, move_target_dir=None, min_width=800, min_height=800, min_size=10000):
    """
    检查某个文件夹下的小图片，并把它们移动到指定文件夹下
    :param source_dir: 需要移动的图片所在路径
    :param move_target_dir: 需要移动到那个文件夹下，如果没有指定则移动到源文件夹的small子文件夹下
    :param min_width: 移动最小宽度
    :param min_height:移动最小高度
    :param min_size:移动最小文件大小，单位为byte
    :return:
    """
    # 如果未指定移动小文件的目标文件夹，则在当前文件夹下生存一个small的子文件夹
    if move_target_dir is None:
        move_target_dir = os.path.join(source_dir, 'small')
        if not os.path.isdir(move_target_dir):
            os.makedirs(move_target_dir)

    image_meta_infos = get_path_illust_meta_infos(source_dir, True)
    log.info('total image file size: {}'.format(len(image_meta_infos)))

    # 通过插画元数据信息进行移动
    for image_meta_info in image_meta_infos:
        if not os.path.isfile(image_meta_info.get('path')):
            log.warn('The file is deleted. path: {}'.format(image_meta_info.get('path')))
            continue

        move_target_path = os.path.join(move_target_dir, image_meta_info.get('file_name'))
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


def move_user_illusts(source_dir: str, user_dir: str, user_id=None, keep_source=True,
                      use_cache=True, replace_user_file=False):
    """
    检查和移动source_dir文件夹下属于某个用户下的图片到目标文件夹
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

    image_meta_infos = get_path_illust_meta_infos(source_dir, use_cache)
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

        log.info('The illust({}) is belong to user_id({}).'.format(image_meta_info.get('illust_id'), user_id))
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


def batch_move_user_illusts():
    base_dir = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'
    check_use_path = r'collect-user'
    check_user_paths = os.listdir(os.path.join(base_dir, check_use_path))
    for check_user_path in check_user_paths:
        move_user_illusts(source_dir=os.path.join(base_dir, r'collect\illusts'),
                          user_dir=os.path.join(base_dir, os.path.join(check_use_path, check_user_path)),
                          keep_source=False, use_cache=True, replace_user_file=True)


def through_user_dir(user_dir: str, use_cache=True) -> dict:
    """
    遍历目标文件夹，获取所有用户信息
    :param user_dir: 用户文件夹
    :param use_cache: 是否使用缓存
    :return:
    """
    cache_file = r'cache\user_illust_info_by_user.json'
    if use_cache and os.path.isfile(cache_file):
        return u_file.load_json_from_file(cache_file)

    log.info('begin through user dir. root path: '.format(user_dir))
    sub_user_dirs = u_file.get_all_sub_files_with_cache(user_dir, contain_dir=True, use_cache=use_cache)
    user_illust_info = {}
    for sub_user_dir in sub_user_dirs:
        user_id = get_illust_id(sub_user_dir)
        if os.path.isdir(sub_user_dir) and user_id >= 0:
            log.info('init user info. user_id: {}, path: {}'.format(user_id, sub_user_dir))
            user_illust_info[user_id] = {
                'user_id': user_id,
                'user_dir': sub_user_dir,
                'db_illusts': query_by_user_id(user_id),
                'download_illusts': os.listdir(sub_user_dir),
                'path_illusts': []
            }

    log.info('end through user dir finished. user_id size: {}'.format(len(user_illust_info)))
    u_file.dump_json_to_file(cache_file, user_illust_info)
    return user_illust_info


def through_illust_dir(illust_dir: str, use_cache=True) -> dict:
    """
    遍历目标文件夹，获取所有图片信息
    :param illust_dir: 图片文件夹
    :param use_cache: 是否使用缓存
    :return:
    """
    cache_file = r'cache\user_illust_info_by_illust.json'
    if use_cache and os.path.isfile(cache_file):
        return u_file.load_json_from_file(cache_file)

    log.info('begin through illust dir. root path: '.format(illust_dir))
    user_illust_info = {}
    sub_illust_files = u_file.get_all_sub_files_with_cache(illust_dir, contain_dir=False, use_cache=use_cache)
    for sub_illust_file in sub_illust_files:
        illust_id = get_illust_id(sub_illust_file)
        if illust_id < 0:
            log.warn('The illust file is not valid. path: {}'.format(sub_illust_file))
            continue

        illustration = get_illustration_by_id(illust_id)
        if not illustration:
            log.warn('The illustration is not exist. illust_id: {}'.format(illust_id))
            continue

        if illustration.user_id not in user_illust_info:
            # 初始化数组
            user_illust_info[illustration.user_id] = {'path_illusts': []}
        user_illust_info[illustration.user_id]['path_illusts'].append(sub_illust_file)

    u_file.dump_json_to_file(cache_file, user_illust_info)
    log.info('end through illust dir. root path: '.format(illust_dir))
    return user_illust_info


def collect_user_illusts(user_dir: str, illust_dir: str, use_cache=True):
    """
    收集用户图片，遍历 illust_dir 下的所有图片，检查是否有图片的作者id是在 user_dir 下的用户的
    :param user_dir: 用户文件夹，可包含多级
    :param illust_dir: 图片文件夹，可包含多级
    :param use_cache: 是否使用缓存
    :return:
    """
    cache_file = r'cache\user_illust_info_merge.json'
    user_dir_info_by_user = through_user_dir(user_dir, use_cache)
    user_dir_info_by_illust = through_illust_dir(illust_dir, use_cache)
    user_dir_info_simple = {}
    not_download_users = []

    # 检查下载的画师，有哪些插画是分散在其他文件夹，已经下载的数量等
    log.info('begin merge user and illust info.')
    for user_id in user_dir_info_by_illust:
        path_illust_ids = list(set(map(lambda x: get_illust_id(x), user_dir_info_by_illust[user_id]['path_illusts'])))

        if user_id in user_dir_info_by_user:
            log.info('merge user illust path. user_id: {}'.format(user_id))
            user_dir_info_by_user[user_id]['path_illusts'] = user_dir_info_by_illust[user_id]['path_illusts']

            download_illust_ids = list(set(map(lambda x: get_illust_id(x), user_dir_info_by_user[user_id]['download_illusts'])))
            user_dir_info_simple[user_id] = {
                'user_id': user_id,
                'user_dir': user_dir_info_by_user[user_id]['user_dir'],
                'count': str(len(user_dir_info_by_user[user_id]['db_illusts'])) + ' -> '
                         + str(len(download_illust_ids)) + ' -> '
                         + str(len(path_illust_ids)),
                # 'db_illust_ids': list(map(lambda x: x['id'], user_dir_info_by_user[user_id]['db_illusts'])),
                # 'download_illust_ids': download_illust_ids,
                # 'path_illust_ids': path_illust_ids
            }
        else:
            not_download_users.append({
                'user_id': user_id,
                'count': len(path_illust_ids),
                'download': is_download_user(user_id),
                'path_illusts': user_dir_info_by_illust[user_id]['path_illusts'],
                'path_illust_ids': path_illust_ids
            })
    log.info('end merge user and illust info.')
    not_download_users.sort(key=lambda x: len(x['path_illust_ids']), reverse=True)
    u_file.dump_json_to_file(cache_file, user_dir_info_by_user)
    u_file.dump_json_to_file(r'cache\user_illust_info_simple.json', user_dir_info_simple)
    u_file.dump_json_to_file(r'cache\not_download_users.json', not_download_users)
    return not_download_users


def process_collect_user_illusts(copy=False):
    base_dir = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'
    user_dir = os.path.join(base_dir, 'collect-user')
    illust_dir = os.path.join(base_dir, 'collect-favorite')
    result = collect_user_illusts(user_dir, illust_dir)

    if not copy:
        return

    # 复制用户文件夹
    for user in result:
        user_dir = os.path.join(base_dir, r'copy-user\{}'.format(user['user_id']))
        u_file.ready_dir(user_dir, is_dir=True)
        if user['count'] < 20:
            log.info('The user illusts size is less than 20. user_id: {}'.format(user['user_id']))
            break

        if is_download_user(user['user_id']):
            log.info('The user has been downloaded. user_id: {}'.format(user['user_id']))
            continue

        log.info('The user illusts is more. user_id: {}, illust size: {}'.format(user['user_id'], user['count']))
        for illust_file in user['path_illusts']:
            if not os.path.isfile(illust_file):
                log.warn('The source illust file is not exist. path: {}'.format(illust_file))
                continue

            if 'old' in illust_file:
                log.info('The illust file contains old keyword, skip it. path: {}'.format(illust_file))
                continue

            user_move_illust_path = os.path.join(user_dir, os.path.basename(illust_file))
            if os.path.isfile(user_move_illust_path):
                log.info('The file is exist. skip it. path: {}'.format(user_move_illust_path))
                continue
            log.info('copy file. from: {} -> {}'.format(illust_file, user_move_illust_path))
            shutil.copy(illust_file, user_move_illust_path)


def check_repeat():
    target_directory = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'
    image_meta_infos = get_path_illust_meta_infos(target_directory)
    log.info('total image meta infos size: {}'.format(len(image_meta_infos)))

    pd.set_option('max_colwidth', 200)  # 设置打印数据宽度
    data_frame = pd.DataFrame(image_meta_infos)

    # 去重
    group_by_illust_id = data_frame.groupby('illust_id')
    log.info('file size: {}, illust size: {}'.format(len(data_frame), len(group_by_illust_id)))
    for illust_id, groups in group_by_illust_id:
        if len(groups) >= 2:
            log.info('The illust is repeat. illust_id: {}'.format(illust_id))
            log.info('\n{}'.format(groups['path']))


def check_download_user(source_dir: str):
    """
    检查目标文件夹中的图片所属用户是否已经下载过
    用来收集那些比较喜欢的图片的作者，然后批量下载这些作者的其他作品
    :param source_dir:
    :return:
    """
    files = u_file.get_all_sub_files(source_dir)
    log.info('sub files size: {}'.format(len(files)))

    not_download_illustrations = []
    for file in files:
        illust_id = get_illust_id(file)
        if illust_id < 0:
            log.warn('The filename not contain illust id. file: {}'.format(file))
            continue
        illustration: Illustration = get_illustration_by_id(illust_id)
        if not illustration:
            log.warn('The illustration is not exist. illust id: {}'.format(illust_id))
            continue

        if is_download_user(illustration.user_id):
            log.info('The illustration user is downloaded. illust_id: {}, user_id: {}'
                     .format(illust_id, illustration.user_id))
            continue

        not_download_illustrations.append(illustration)
    log.info('not download user illustration size: {}'.format(len(not_download_illustrations)))
    not_download_illustrations.sort(key=lambda x: x.user_id)
    content = ''
    user_id_count = {}
    for illust in not_download_illustrations:
        user_id_count[illust.user_id] = user_id_count.get(illust.user_id, 0) + 1
        content += str(illust.user_id) + ': ' + str(illust.id) + '\n'
    print(user_id_count)
    u_file.write_content('user_illust.txt', content)


if __name__ == '__main__':
    # illust_id = 60881929
    # user_id = get_user_id_by_illust_id(illust_id)

    # user_id = 935581
    # collect_illusts(str(user_id), is_special_illust_ids, 1000, user_id=user_id, use_cache=False)
    # move_small_file(r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\by-user\3302692',
    #                 use_cache=False, min_width=1800, min_height=1800,
    #                 move_directory=r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\small')
    # check_download_user(r'G:\漫画\pixiv\hight-4-star')
    process_collect_user_illusts()
