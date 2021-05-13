#!/usr/bin/python
# -*- coding: utf-8 -*
# file function


import os
import time
import json
import urllib.parse
import requests
import threadpool
from PIL import Image

import u_base.u_log as log

__all__ = [
    'get_content',
    'get_json',
    'read_content',
    'write_content',
    'get_file_name_from_url',
    'download_image',
    'download_file',
    'download_by_pool',
    'convert_image_format',
    'get_all_sub_files',
    'parse_json',
    'cache_json',
    'load_json_from_file'
]

COMMON_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/88.0.4324.146 Safari/537.36'
}


def get_content(path):
    """
    read content from file or url
    :param path: file or url
    :return: file or url content
    """
    if not path:
        return False
    # if path is file, read from file
    if os.path.isfile(path):
        log.info('read content from file: {}'.format(path))
        fin = open(path, 'r', encoding='UTF-8')
        html_content = fin.read()
        fin.close()
        return html_content
    try:
        # herders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}
        log.info('begin get info from web url: ' + path)
        # time.sleep(0.5)
        response = requests.get(path, timeout=60)
        log.info('end get info from web url: ' + path)
        if not (400 <= response.status_code < 500):
            response.raise_for_status()
        return response.text
    except Exception as e:
        log.info('get content fail. {}'.format(e))
        return False


def get_json(url, params=None, headers=None) -> dict:
    """
    request json from url
    :param url: url
    :param params: params
    :param headers: headers
    :return: json
    """
    try:
        response = requests.get(url, params=params, headers=headers)
    except Exception as e:
        log.warn('request error and try again. {}'.format(e))
        response = requests.get(url, params=params, headers=headers)
    return json.loads(response.text)


def read_content(file_path):
    """
    read content from file, use UTF-8 encoding
    :param file_path: target file path
    :return: file content
    """
    if not os.path.isfile(file_path):
        log.warn('The file is not exist')
        return None
    log.info('read content from file: {}'.format(file_path))
    fin = open(file_path, 'r', encoding='UTF-8')
    content = fin.read()
    fin.close()
    return content


def read_file_as_list(file_path: str) -> list:
    """
    按行读取文件，并返回list，每一个元素是每一行记录
    :param file_path: 文件绝对地址
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


def write_content(file_path, content) -> str:
    """
    write content to file, use UTF-8 encoding and overwrite
    :param file_path: target file path
    :param content: write content
    :return: file_path
    """
    dir_path = os.path.dirname(file_path)
    if not os.path.isdir(dir_path):
        log.info('the file path is not exist. create: {}'.format(dir_path))
    fout = open(file_path, 'w', encoding='UTF-8')
    fout.write(content)
    fout.close()
    return file_path


# download image from url
def download_image(url, path=os.path.curdir, name=None, replace=False, prefix=''):
    """
    download image from url
    :param url: image_url
    :param prefix: image name prefix
    :param path: save directory path
    :param name: image name
    :param replace: replace the same name file.
    :return:
    """
    if not name:
        name = prefix + os.path.basename(url)
    else:
        name = prefix + name

    image_path = os.path.join(path, name)
    if os.path.exists(image_path) and not replace:
        log.info('The file is exist and not replace: {}'.format(image_path))
        return True

    # Write stream to file
    log.info('begin download image from url: {}'.format(url))
    try:
        response = requests.get(url, stream=True)
        with open(image_path, 'wb') as out_file:
            out_file.write(response.content)
        del response
    except Exception as e:
        log.error('download image file. {}'.format(e))
        return False
    log.info('end download image. save file: {}'.format(image_path))
    return True


def get_file_name_from_url(url):
    file_name = os.path.basename(url)
    return urllib.parse.unquote(file_name)


def download_file(url, file_name, path=os.path.curdir, replace=False, **kwargs):
    """
    download file from url
    :param url: image_url
    :param path: save directory path
    :param file_name: image name
    :param replace: replace the same name file.
    :return:
    """
    if not file_name:
        file_name = os.path.basename(url)
    elif os.path.splitext(file_name)[-1].find('.') < 0:
        # 所给文件名不带后缀的话，添加上后缀
        file_name += os.path.splitext(url)[-1]

    # 指定文件夹不存在则创建
    if not os.path.isdir(path):
        os.makedirs(path)

    file_name = file_name[:200]  # windows文件名称不能超过255个字符
    file_path = os.path.join(path, file_name)

    # 如果文件已经下载并且不替换，则直接结束
    if os.path.exists(file_path) and not replace:
        log.info('The file is exist and not replace: {}'.format(file_path))
        return True

    # Write stream to file
    log.info('begin download file from url: {}'.format(url))
    try:
        response = requests.get(url, stream=True, headers=COMMON_HEADERS, **kwargs)
        with open(file_path, 'wb') as out_file:
            out_file.write(response.content)
        del response
    except Exception as e:
        log.error('download file file. {}'.format(e))
        return False
    log.info('end download file. save file: {}'.format(file_path))
    return True


# 使用线程池并行下载
def download_by_pool(directory, urls=None, pool_size=8):
    # 创建文件夹
    if not os.path.exists(directory):
        os.makedirs(directory)
    log.info('begin download image, url size: ' + str(len(urls)))
    pool = threadpool.ThreadPool(pool_size)
    params = map(lambda v: (None, {'directory': directory, 'url': v}), urls)
    task_list = threadpool.makeRequests(download_file, params)
    [pool.putRequest(task) for task in task_list]
    pool.wait()


def convert_image_format(image_path, delete=False):
    """
    转换WEBP的图片格式到JPEG
    :param image_path: 图片地址，最好是绝对路径
    :param delete: 是否删除原来的图片
    :return:
    """
    if not os.path.isfile(image_path):
        log.warn('The image is not exist. path: {}'.format(image_path))
        return None
    image = Image.open(image_path)
    image_format = image.format
    # 如果是webp格式转为jpeg格式
    if image_format == 'WEBP':
        image.save(image_path, 'JPEG')
    image.close()
    if delete:
        os.remove(image_path)


def get_all_sub_files(root_path, all_files=None, contain_dir=False):
    """
    递归获取所有子文件列表
    :param root_path: 递归根目录
    :param all_files: 递归过程中的所有文件列表
    :param contain_dir: 返回值是否包含目录
    :return:
    """
    if all_files is None:
        all_files = []

    # root_path 不是目录直接返回file_list
    if not os.path.isdir(root_path):
        return all_files
    else:
        log.info('begin through path: {}'.format(root_path))

    # 获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_or_file in dir_or_files:
        dir_or_file = os.path.join(root_path, dir_or_file)  # 拼接得到完整路径

        if os.path.isdir(dir_or_file):
            # 如果是文件夹，则递归遍历
            if contain_dir:
                all_files.append(dir_or_file)
            get_all_sub_files(dir_or_file, all_files, contain_dir)
        else:
            # 否则将当前文件加入到 all_files
            all_files.append(os.path.abspath(dir_or_file))
    return all_files


def parse_json(json_str):
    """parse json str into dict"""
    return json.loads(json_str)


def cache_json(json_data, cache_file=None) -> str:
    if not cache_file:
        cache_file = os.path.join(os.getcwd(), 'cache')
        cache_file = os.path.join(cache_file, 'cache-' + time.strftime('%Y-%m-%d-%H-%M-%S',
                                                                       time.localtime(time.time())) + '.json')
    cache_file_dir = os.path.split(cache_file)[0]
    if not os.path.isdir(cache_file_dir):
        os.makedirs(cache_file_dir)
    json.dump(json_data, open(cache_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return cache_file


def dump_json_to_file(json_file, json_data):
    file_handle = open(json_file, 'w', encoding='utf-8')
    json.dump(json_data, file_handle, ensure_ascii=False, indent=4)
    file_handle.close()


def load_json_from_file(json_file):
    file_handle = open(json_file, encoding='utf-8')
    json_data = None
    if os.path.isfile(json_file):
        json_data = json.load(file_handle)
    file_handle.close()
    return json_data
