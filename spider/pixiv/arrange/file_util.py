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
    'get_all_image_paths'
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


def get_all_image_paths(image_directory: str, use_cache: bool = True, contain_dir=False) -> list:
    """
    递归获取某个文件夹下的所有图片和文件夹
    :param image_directory: 图片路径
    :param use_cache: 是否使用缓存
    :param contain_dir: 返回值是否包含目录
    :return: 图片绝对路径列表
    """
    log.info('begin get all image files from path: {}'.format(image_directory))
    if not os.path.isdir(image_directory):
        log.error('The image directory is not exist: {}'.format(image_directory))
        return []

    # 构建cache文件夹并检查是否存在cache
    cache_file_path = get_cache_path(image_directory, 'image_paths', 'txt')
    cache_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cache_file_path)
    if use_cache and os.path.isfile(cache_file_path):
        # 存在缓存文件直接使用缓存
        log.info('read all image file from cache: {}'.format(cache_file_path))
        return u_file.read_file_as_list(cache_file_path)

    # 如果cache目录不存在，则创建
    if not os.path.isdir(os.path.split(cache_file_path)[0]):
        log.info('create the cache directory: {}'.format(cache_file_path))
        os.makedirs(os.path.split(cache_file_path)[0])
    all_files = u_file.get_all_sub_files(image_directory, contain_dir=contain_dir)

    # 将结果存入cache
    cache_file_path_handler = open(cache_file_path, 'w+', encoding='utf-8')
    for file in all_files:
        cache_file_path_handler.writelines(file + '\n')
    cache_file_path_handler.close()
    log.info('get_all_image_files finish. file size: {}'.format(len(all_files)))
    return all_files


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
