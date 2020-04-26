"""
该文件主要是一些文件处理函数
"""

import os
import re
import u_base.u_log as log


__all__ = [
    'get_base_path',
    'read_file_as_list',
    'get_all_image_file_path',
    'get_illust_file_path',
    'get_illust_id',
    'collect_illust',
    'get_directory_illusts',
    'get_all_sub_files',
    'get_all_image_paths'
]


def get_base_path(path_name: str = None):
    """
    返回所有相对illust处理的基础路径，使用绝对路径，避免在不同地方调用时路径错误
    :param path_name: path名词，
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


def read_file_as_list(file_path: str) -> list:
    """
    按行读取文件，并返回list，每一个元素是每一行记录
    :param file_path:
    :return:
    """
    if not os.path.isfile(file_path):
        log.warn('The file is not exist. {}'.format(file_path))
        return []
    file_handle = open(file_path, 'r', encoding='utf-8')
    line = file_handle.readline()
    contents = set()
    while line:
        line = line.strip('\n')
        contents.add(line)
        line = file_handle.readline()
    file_handle.close()
    log.info('read file end. list size: {}'.format(len(contents)))
    return list(contents)


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
    log.warn('The illust_id is not error. illust_file: {}'.format(illust_file_path))
    return -1


def get_all_image_file_path(use_cache: bool = True) -> list:
    """
    获取所有的图片文件路径列表
    :type use_cache: bool 是否使用cache
    :return: 图片路径列表
    """
    log.info('begin read all image file illusts')
    cache_file_path = r'cache\all_image_file.txt'
    cache_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cache_file_path)
    if use_cache and os.path.isfile(cache_file_path):
        # 存在缓存文件直接使用缓存
        log.info('read all image file from cache: {}'.format(cache_file_path))
        return read_file_as_list(cache_file_path)

    # 如果cache目录不存在，则创建
    if not os.path.isdir(os.path.split(cache_file_path)[0]):
        log.info('create the cache directory: {}'.format(cache_file_path))
        os.makedirs(os.path.split(cache_file_path)[0])

    cache_file_path_handler = open(cache_file_path, 'w+', encoding='utf-8')
    illust_file_paths = set()
    base_directory = get_base_path('illusts')
    illust_directories = ['10000-20000', '20000-30000', '30000-40000', '40000-50000', '5000-6000',
                          '6000-7000', '7000-8000', '8000-9000', '9000-10000', 'r-18']
    for illust_directory in illust_directories:
        illust_directory = base_directory + '\\' + illust_directory
        if not os.path.isdir(illust_directory):
            log.warn('The directory is not exist: {}'.format(illust_directory))
            continue
        illust_files = os.listdir(illust_directory)
        log.info('illust_directory: %s, illust files size: %d' % (illust_directory, len(illust_files)))
        for illust_file in illust_files:
            full_source_illust_file_path = os.path.join(illust_directory, illust_file)       # 完整的源图片路径
            full_source_illust_file_path = os.path.abspath(full_source_illust_file_path)
            if os.path.isdir(full_source_illust_file_path):
                # 目录不用处理
                continue
            illust_file_paths.add(full_source_illust_file_path)
            cache_file_path_handler.writelines(full_source_illust_file_path + '\n')
    log.info('The illust image file size: {}'.format(len(illust_file_paths)))
    # illust_list_file_handle.close()
    return list(illust_file_paths)


def get_all_image_paths(image_directory: str, use_cache: bool = True) -> list:
    """
    递归获取某个文件夹下的所有图片
    :param image_directory: 图片路径
    :param use_cache: 是否使用缓存
    :return: 图片绝对路径列表
    """
    log.info('begin get all image files from path: {}'.format(image_directory))
    if not os.path.isdir(image_directory):
        log.error('The image directory is not exist: {}'.format(image_directory))
        return []
    cache_file_path = r'cache\file-cache-' + re.sub(r"[\\/?*<>|\":]+", '-', image_directory) + '.txt'
    cache_file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), cache_file_path)
    if use_cache and os.path.isfile(cache_file_path):
        # 存在缓存文件直接使用缓存
        log.info('read all image file from cache: {}'.format(cache_file_path))
        return read_file_as_list(cache_file_path)
    # 如果cache目录不存在，则创建
    if not os.path.isdir(os.path.split(cache_file_path)[0]):
        log.info('create the cache directory: {}'.format(cache_file_path))
        os.makedirs(os.path.split(cache_file_path)[0])
    all_files = get_all_sub_files(image_directory)
    cache_file_path_handler = open(cache_file_path, 'w+', encoding='utf-8')
    for file in all_files:
        cache_file_path_handler.writelines(file + '\n')
    cache_file_path_handler.close()
    log.info('get_all_image_files finish. file size: {}'.format(len(all_files)))
    return all_files


def get_all_sub_files(root_path, all_files=None):
    """
    递归获取所有子文件列表
    :param root_path: 递归根目录
    :param all_files: 递归过程中的所有文件列表
    :return:
    """
    if all_files is None:
        all_files = []

    # root_path 不是目录直接返回file_list
    if not os.path.isdir(root_path):
        return all_files

    # 获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_or_file in dir_or_files:
        dir_or_file = os.path.join(root_path, dir_or_file)  # 拼接得到完整路径

        if os.path.isdir(dir_or_file):
            # 如果是文件夹，则递归遍历
            get_all_sub_files(dir_or_file, all_files)
        else:
            # 否则将当前文件加入到 all_files
            all_files.append(os.path.abspath(dir_or_file))
    return all_files


def get_illust_file_path(illust_id: int) -> str:
    """
    查询指定illust_id文件所在的地址
    :param illust_id: 给定的插图id
    :return: 如果找到，返回该图片的绝对地址，否则返回None
    """
    illust_file_paths = get_all_image_file_path()
    for illust_file_path in illust_file_paths:
        illust_filename = os.path.split(illust_file_path)[1]
        current_illust_id = illust_filename.split('_')[0]
        if current_illust_id.isdigit() and int(current_illust_id) == illust_id:
            return illust_file_path
    log.error("The illust file is not exist. illust_id: {}".format(illust_id))
    return None


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


def get_directory_illusts(illust_directory) -> list:
    """
    获取某个文件夹下的所有插簧，适用于pixiv插画
    :param illust_directory: 插画路径
    :return: 插画信息列表
    """
    illusts = []
    if not os.path.isdir(illust_directory):
        log.error('The illust directory is not exist: {}'.format(illust_directory))
        return illusts
    illust_files = os.listdir(illust_directory)
    for illust_file in illust_files:
        illust_file = os.path.join(illust_directory, illust_file)
        if os.path.isdir(illust_file):
            log.info('The file is directory: {}'.format(illust_file))
            continue
        illust_id = get_illust_id(illust_file)
        if illust_id is None:
            log.info('The file illust_id is None: {}'.format(illust_file))
            continue
        illusts.append({
            'illust_id': illust_id,
            'path': os.path.abspath(illust_file)
        })
    log.info('read all illusts success. size: {}'.format(len(illusts)))
    return illusts


if __name__ == '__main__':
    get_all_image_file_path(False)
