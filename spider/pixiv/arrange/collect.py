#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from u_base.u_log import logger as log
import u_base.u_file as u_file
from spider.pixiv.arrange.file_util import collect_illust, get_illust_id
from spider.pixiv.mysql.db import session, Illustration, update_illustration_tag, update_user_tag

__all__ = [
    'update_dir_illust_tag',
    'extract_top',
    'collect_illusts'
]


# 用来缓存一批 illust_id
cache_illust_ids = []


# 更新本地整理好的插图
def update_dir_illust_tag(directory: str, tag: str):
    """
    将某个文件夹下的所有文件在illust数据库中的记录标记tag
    :param directory: 目标文件夹
    :param tag: 某个类型的标记名称，
               ignore: 校验过不需要的插画
               downloaded： 已经下载的图片
               small: 图片太小
               delete: 直接删除
               too_long: 太长啦，一般是那种漫画类
               gray: 黑白插画
    :return: None
    """
    if not os.path.exists(directory):
        log.error('The directory is not exist: {}'.format(directory))
        return
    illust_files = os.listdir(directory)
    for illust_file in illust_files:
        # 获取目录或者文件的路径
        if os.path.isdir(os.path.join(directory, illust_file)):
            continue
        log.info('process file: ' + illust_file)
        # 提取 illust_id
        illust_id = get_illust_id(illust_file)
        if illust_id <= 0:
            log.warn('The file illust_id is not exist. file: {}'.format(illust_file))
            continue
        update_illustration_tag(illust_id, tag)
        # os.remove(os.path.join(directory, illust_file))
    log.info('process end. total illust size: {}'.format(len(illust_files)))


def update_sub_dir_illust_tag(parent_directory, tag):
    """
    将某个文件夹下的所有文件在illust数据库中的记录标记tag，支持两级文件夹
    :param parent_directory: 父级文件夹
    :param tag: 需要更新的标签
    :return: None
    """
    child_directories = os.listdir(parent_directory)
    for directory in child_directories:
        directory = os.path.join(parent_directory, directory)
        log.info('begin process directory: {}'.format(directory))
        update_dir_illust_tag(directory, tag)


def update_dir_user_tag(source_dir, tag, replace=True):
    """
    更新source_dir文件夹下的所有子文件夹中的user_id的标签
    :param source_dir: 需要处理的文件夹
    :param tag: 更新的标签，如download,favorite
    :param replace: 是否替换原来的标签
    :return: None
    """
    if not os.path.exists(source_dir):
        log.error('The directory is not exist: {}'.format(source_dir))
        return
    paths = os.listdir(source_dir)
    for path in paths:
        # 用户都是文件夹
        if not os.path.isdir(os.path.join(source_dir, path)):
            continue
        user_id = get_illust_id(path)
        if user_id <= 0:
            log.warn('The file illust_id is not exist. file: {}'.format(path))
            continue
        update_user_tag(user_id, tag, replace=True)


# 提取某个文件夹下面收藏TOP的图片
def extract_top(illust_path: str, count: int):
    if not os.path.isdir(illust_path):
        log.error('The illust path is not exist: {}'.format(illust_path))
        return
    illust_files = os.listdir(illust_path)
    log.info('The illust size is: {}'.format(len(illust_files)))

    # top子文件夹
    top_directory = os.path.join(illust_path, 'top')
    if not os.path.isdir(top_directory):
        log.info('create top directory: {}'.format(top_directory))
        os.makedirs(top_directory)

    # 查询子文件夹下的所有插画信息
    illustrations: [Illustration] = []
    for illust_file in illust_files:
        if os.path.isdir(illust_file):
            log.info('The file is directory: {}'.format(illust_file))
            continue
        illust_id = get_illust_id(illust_file)
        if illust_id <= 0:
            log.error('The illust_id is is not exist: {}'.format(illust_file))
            continue
        illustrations.append(session.query(Illustration).get(illust_id))

    # 按照收藏倒序排序，并取前面 count 个
    illustrations.sort(key=lambda x: x.total_bookmarks, reverse=True)
    illustrations = illustrations[:count]
    top_illust_ids = set(x.id for x in illustrations)
    log.info('The top illust ids is: {}'.format(top_illust_ids))

    # 将top收藏的插画移动到top文件夹
    for illust_file in illust_files:
        if get_illust_id(illust_file) in top_illust_ids:
            log.info('ready move top file: {}'.format(illust_file))
            source_file_path = os.path.join(illust_path, illust_file)
            source_file_path = os.path.abspath(source_file_path)
            move_target_path = os.path.join(top_directory, illust_file)
            move_target_path = os.path.abspath(move_target_path)
            log.info('move file: {} --> {}'.format(source_file_path, move_target_path))
            os.replace(source_file_path, move_target_path)


# 移动、统一、分类文件
def collect_illusts(collect_tag='back', collect_function=None, max_collect_count=10, **kwargs):
    """
    将满足某个条件的插画全部移动到指定的收藏文件夹
    :param collect_tag:
    :param collect_function:
    :param max_collect_count:
    :param kwargs:
    :return:
    """
    log.info('begin collect illusts. tag: {}, max_collect_count: {}'.format(collect_tag, max_collect_count))
    default_kwargs = {
        'target_directory': r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result',
        'use_cache': True
    }
    default_kwargs.update(kwargs)
    kwargs = default_kwargs

    illust_paths = u_file.get_all_sub_files_with_cache(kwargs.get('target_directory'), use_cache=kwargs.get('use_cache'))
    collect_count = 0
    for illust_path in illust_paths:
        if not os.path.isfile(illust_path):
            log.warn('The file is not exist: {}'.format(illust_path))
            continue
        if collect_function(illust_path):
            collect_illust(collect_tag, illust_path)
            collect_count += 1
        if collect_count >= max_collect_count:
            break
    log.info('----> total move file count: {}'.format(collect_count))


if __name__ == '__main__':
    # illust_id = 60881929
    # user_id = get_user_id_by_illust_id(illust_id)
    # base_dir = r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result'

    # user_id = 935581
    # collect_illusts('invalid', collect_function=is_small_size, max_collect_count=1000)   # 无效图片
    # collect_illusts(user_id, is_special_illust_ids, 1000, use_cache=False)
    # collect_illusts(r'ignore', is_small_size, 10)  # ゴスロリ  雪  バロック世界  ワンピース服  動物擬人化 雪風  セーラー服
    update_dir_illust_tag(r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\ignore', 'ignore')
    # update_dir_user_tag(r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\ignore', 'download')
    # update_dir_user_tag(r'G:\Projects\Python_Projects\python-base\spider\pixiv\crawler\result\ignore', 'ignore')
    # check_user_id(target_directory)
    # extract_top(target_directory, 20)
