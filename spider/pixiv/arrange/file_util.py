"""
该文件主要是一些文件处理函数
"""

import os
import re
import u_base.u_log as log
import u_base.u_file as u_file


__all__ = [
    'is_special_tag',
    'is_small_size',
    'get_cache_path',
    'get_base_path',
    'get_illust_id',
    'collect_illust',
]


# 是否指定的tag
def is_special_tag(illust_path: str) -> bool:
    move_tags = ['wlop', 'wlop']
    illust_filename = os.path.split(illust_path)[1]
    tags = illust_filename.split('-')  # 从文件名分解得出包含的标签
    for tag in tags:
        for move_tag in move_tags:
            if tag.find(move_tag) >= 0:
                return True
    return False


# 是否图片长宽太小或者文件太小
def is_small_size(illust_path: str, min_file_size=5e5) -> bool:
    return os.path.getsize(illust_path) <= min_file_size


def get_cache_path(source_dir, tag='default', extension='txt'):
    base_dir = r'cache\cache-' + tag + re.sub(r"[\\/?*<>|\":]+", '-', source_dir) + '.' + extension
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), base_dir)


def get_base_path(path_name: str = None):
    """
    返回所有相对illust处理的基础路径，使用绝对路径，避免在不同地方调用时路径错误
    :param path_name: 相对路径，
    :return:
    """
    base_path = os.path.abspath(os.path.dirname(__file__))
    base_path = os.path.join(base_path, r'..\crawler\result')
    if not os.path.isdir(path_name):
        log.info('The path_name is not exist, create it. path_name: {}'.format(path_name))
        base_path = os.path.join(base_path, path_name)
        if not os.path.isdir(base_path):
            log.info('Create the base path: {}'.format(base_path))
            os.makedirs(base_path)
    return os.path.abspath(base_path)


def get_illust_id(illust_file_path: str) -> int:
    """
    通过文件名，提取插画pixiv_id
    :param illust_file_path: 插画路径，可以使相对路径，绝对路径或者文件名
    :return: 插画id，如果没有则返回-1
    """
    illust_filename = os.path.split(illust_file_path)[1]
    illust_id = illust_filename.split('_')[0]
    if illust_id.isdigit():
        return int(illust_id)
    illust_id = illust_filename.split('-')[0]
    if illust_id.isdigit():
        return int(illust_id)
    log.warn('The illust_id is error. illust_file: {}'.format(illust_file_path))
    return -1


def collect_illust(collect_name, source_illust_file_path):
    """
    收藏插画，适用于pixiv下载图片
    :param collect_name: 收藏tag，如果是存在的路径则将图片移动到该路径，如果只是简单name，那么使用默认路径
    :param source_illust_file_path: 原始插画地址
    :return: None
    """
    move_target_directory = collect_name
    if not os.path.isdir(move_target_directory):
        # 如果collect_name不是路径，收藏到默认路径
        move_target_directory = get_base_path('collect')
        move_target_directory = os.path.join(move_target_directory, collect_name)

    if not os.path.isdir(move_target_directory):
        # 文件不存在则创建
        os.makedirs(move_target_directory)
    move_target_file_path = os.path.join(move_target_directory, os.path.split(source_illust_file_path)[1])

    move_target_file_path = os.path.abspath(move_target_file_path)
    source_illust_file_path = os.path.abspath(source_illust_file_path)
    if os.path.isfile(source_illust_file_path):
        log.info('move file from: {} ---> {}'.format(source_illust_file_path, move_target_file_path))
        os.replace(source_illust_file_path, move_target_file_path)


if __name__ == '__main__':
    get_illust_id(r'2352')
