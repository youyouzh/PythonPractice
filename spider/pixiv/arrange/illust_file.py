"""
该文件主要是一些文件处理函数
"""

import os
import u_base.u_log as log


__all__ = [
    'read_file_as_list',
    'get_all_image_file_path',
    'get_illust_file_path',
    'get_illust_id',
    'collect_illust',
    'get_directory_illusts'
]


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
    illust_filename = os.path.split(illust_file_path)[1]
    illust_id = illust_filename.split('_')[0]
    if illust_id.isdigit():
        return int(illust_id)
    log.warn('The illust_id is not error. illust_file: {}'.format(illust_file_path))
    return -1


def get_all_image_file_path() -> list:
    """
    获取所有的图片文件路径列表
    :return: 图片路径列表
    """
    log.info('begin read all image file illusts')
    illust_list_save_path = r'cache\all_image_file.txt'
    illust_list_save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), illust_list_save_path)
    if os.path.isfile(illust_list_save_path):
        # 存在缓存文件直接使用缓存
        log.info('read all image file from cache: {}'.format(illust_list_save_path))
        return read_file_as_list(illust_list_save_path)

    # 遍历目录
    if not os.path.isdir(os.path.split(illust_list_save_path)[0]):
        log.info('create the cache directory: {}'.format(illust_list_save_path))
        os.makedirs(os.path.split(illust_list_save_path)[0])

    illust_list_file_handle = open(illust_list_save_path, 'w+', encoding='utf-8')
    illust_file_paths = set()
    base_directory = r'..\crawler\result\illusts'
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
            illust_list_file_handle.writelines(full_source_illust_file_path + '\n')
    log.info('The illust image file size: {}'.format(len(illust_file_paths)))
    # illust_list_file_handle.close()
    return list(illust_file_paths)


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
    move_target_directory = collect_name
    if not os.path.isdir(move_target_directory):
        # 如果collect_name不是路径，收藏到默认路径
        move_target_directory = r'..\crawler\result\collect\1111-r-18'
        move_target_directory = os.path.join(move_target_directory, collect_name)

    if not os.path.isdir(move_target_directory):
        os.makedirs(move_target_directory)
    move_target_file_path = os.path.join(move_target_directory, os.path.split(source_illust_file_path)[1])

    move_target_file_path = os.path.abspath(move_target_file_path)
    source_illust_file_path = os.path.abspath(source_illust_file_path)
    if os.path.isfile(source_illust_file_path):
        log.info('move file from: {} ---> {}'.format(source_illust_file_path, move_target_file_path))
        os.replace(source_illust_file_path, move_target_file_path)


def get_directory_illusts(illust_directory) -> list:
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
    get_all_image_file_path()

