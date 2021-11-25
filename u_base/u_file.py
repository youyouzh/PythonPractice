#!/usr/bin/python
# -*- coding: utf-8 -*
# file function


import os
import time
import json
import re
import urllib.parse
import requests
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED


import u_base.u_log as log

__all__ = [
    'convert_windows_path',
    'get_file_name_from_url',
    'covert_url_to_filename',
    'get_abs_cache_path',
    'ready_dir',
    'get_content_with_cache',
    'get_content',
    'get_json',
    'read_content',
    'read_file_as_list',
    'write_content',
    'download_file',
    'download_files_with_pool',
    'convert_image_format',
    'get_all_sub_files_with_cache',
    'get_all_sub_files',
    'cache_json',
    'dump_json_to_file',
    'load_json_from_file',
    'extract_init_json_data',
    'COMMON_USER_AGENT',
    'm_get'
]

COMMON_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Chrome/96.0.4664.45 Safari/537.36'
COMMON_HEADERS = {
    'user-agent': COMMON_USER_AGENT
}


def convert_windows_path(path):
    """
    将path中的特殊字符进行替换，转成Windows兼容的路径
    :param path: 原始路径
    :return: 转换后的路径
    """
    return re.sub(r"[\\/?*<>|\":]+", '-', path)


def get_file_name_from_url(url):
    """
    从url中获取文件名，适用于带后缀的url
    :param url: 带后缀的url
    :return: 文件名
    """
    file_name = os.path.basename(url)
    return urllib.parse.unquote(file_name)


def covert_url_to_filename(url):
    """
    将url转化为文件名，一帮用于缓存文件生成
    :param url: url
    :return: filename
    """
    parse_result = urllib.parse.urlsplit(url)
    file_name = parse_result.netloc + parse_result.path + parse_result.query
    file_name = convert_windows_path(file_name)
    return file_name


def get_abs_cache_path():
    """
    获取cache文件夹的绝对路径，方便缓存文件
    :return:
    """
    return os.path.join(os.getcwd(), 'cache')


def ready_dir(file_path: str):
    """
    准备相关文件夹，检查path所在文件夹是否存在，若不存在则创建
    :param file_path: 文件路径，不能是文件夹路径
    :return: None
    """
    dir_path = os.path.dirname(file_path)
    if not os.path.isdir(dir_path):
        log.info('the file path is not exist. create: {}'.format(dir_path))
        os.makedirs(dir_path)


def get_content_with_cache(url: str, cache_file: str = None, use_cache=True, encoding=None, **kwargs):
    if use_cache:
        # 没有指定缓存文件则从url中生成缓存文件
        if cache_file is None:
            cache_file = os.path.join(get_abs_cache_path(), covert_url_to_filename(url))
            cache_file = cache_file + '.txt'

        # 如果缓存文件存在，则直接返回缓存文件内容
        if os.path.isfile(cache_file):
            log.info('load content from cache: {}'.format(cache_file))
            return read_content(cache_file)
    html_content = get_content(url, encoding, **kwargs)
    if html_content:
        ready_dir(cache_file)
        write_content(cache_file, html_content)
    return html_content


def get_content(path, encoding=None, retry=0, **kwargs):
    """
    从文件中或者url中读取内容
    :param path: 文件路径或者url
    :param encoding: 返回值编码
    :param retry: 重试次数
    :return: 文件内容或者url返回值
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
        log.info('begin get info from web url: ' + path)

        # 合并公用头部
        default_headers = {}
        default_headers.update(COMMON_HEADERS)
        if kwargs.get('headers') is not None:
            default_headers.update(kwargs.get('headers'))
        kwargs['headers'] = default_headers

        response = requests.get(path, timeout=60, **kwargs)
        if encoding is not None:
            response.encoding = encoding

        log.info('end get info from web url: ' + path)
        if not (400 <= response.status_code < 500):
            response.raise_for_status()
        if response.text is None or response.text == '':
            log.error('The response text is empty.')
        return response.text
    except Exception as e:
        log.error('get url content error. url: {}, error: {}'.format(path, e))
        if retry > 0:
            # 重试
            log.info('retry get content. left times: {}'.format(retry - 1))
            return get_content(path, encoding, retry - 1, **kwargs)
        log.info('get content failed. {}'.format(e))
        return False


def get_json(url, params=None, headers=None, **kwargs) -> dict:
    """
    request json from url
    :param url: url
    :param params: params
    :param headers: headers
    :return: json
    """
    default_headers = {}
    default_headers.update(COMMON_HEADERS)
    if headers is not None:
        default_headers.update(headers)
    try:
        response = requests.get(url, params=params, headers=default_headers, **kwargs)
    except Exception as e:
        log.warn('request error and try again. {}'.format(e))
        response = requests.get(url, params=params, headers=default_headers, **kwargs)
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
    ready_dir(file_path)
    fout = open(file_path, 'w', encoding='UTF-8')
    fout.write(content)
    fout.close()
    return file_path


def download_file(url, filename, path=os.path.curdir, replace=False, **kwargs):
    """
    download file from url
    :param url: image_url
    :param path: save directory path
    :param filename: image name
    :param replace: replace the same name file.
    :return:
    """
    if not filename:
        filename = os.path.basename(url)
    elif os.path.splitext(filename)[-1].find('.') < 0:
        # 所给文件名不带后缀的话，添加上后缀
        filename += os.path.splitext(url)[-1]

    # 指定文件夹不存在则创建
    filename = filename[:200]  # windows文件名称不能超过255个字符
    file_path = os.path.join(path, filename)
    ready_dir(file_path)

    # 如果文件已经下载并且不替换，则直接结束
    if os.path.exists(file_path) and not replace:
        log.info('The file is exist and not replace: {}'.format(file_path))
        return True

    # Write stream to file
    log.info('begin download file from url: {}, save filename: {}'.format(url, filename))
    try:
        response = requests.get(url, stream=True, headers=COMMON_HEADERS, **kwargs)
        with open(file_path, 'wb') as out_file:
            out_file.write(response.content)
        del response
    except Exception as e:
        log.error('download file failed. {}'.format(e))
        return False
    log.info('end download file. save file: {}'.format(file_path))
    return True


def download_files_with_pool(urls: list, path, replace=False, **kwargs):
    pool = ThreadPoolExecutor(10)
    tasks = []
    for url in urls:
        filename = get_file_name_from_url(urls)
        future = pool.submit(download_file, url, filename, path, replace=replace, **kwargs)
        tasks.append(future)

    wait(tasks, return_when=ALL_COMPLETED)
    log.info('all file download task pool finished.')


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


def get_all_sub_files_with_cache(root_path, contain_dir=False, use_cache=True):
    cache_file = os.path.join(get_abs_cache_path(), convert_windows_path(root_path))
    if use_cache and os.path.isfile(cache_file):
        log.info('load content from cache: {}'.format(cache_file))
        return load_json_from_file(cache_file)
    else:
        ready_dir(cache_file)
        sub_files = get_all_sub_files(root_path, contain_dir=contain_dir)
        cache_json(sub_files, cache_file)
        return sub_files


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


def cache_json(json_data, cache_file=None) -> str:
    """
    缓存json数据
    :param json_data: json data
    :param cache_file: cache file, auto generate
    :return: cache file path
    """
    if not cache_file:
        cache_file = get_abs_cache_path()
        cache_file = os.path.join(cache_file, 'cache-' + time.strftime('%Y-%m-%d-%H-%M-%S',
                                                                       time.localtime(time.time())) + '.json')
    ready_dir(cache_file)
    json.dump(json_data, open(cache_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
    return cache_file


def dump_json_to_file(json_file, json_data):
    """
    将json数据存入文件中
    :param json_file:
    :param json_data:
    :return:
    """
    ready_dir(json_file)
    file_handle = open(json_file, 'w', encoding='utf-8')
    json.dump(json_data, file_handle, ensure_ascii=False, indent=4)
    file_handle.close()


def load_json_from_file(json_file) -> dict:
    """
    从文件中加载json数据
    :param json_file:
    :return:
    """
    file_handle = open(json_file, encoding='utf-8')
    json_data = None
    if os.path.isfile(json_file):
        json_data = json.load(file_handle)
    file_handle.close()
    return json_data


def extract_init_json_data(html_content: str, pattern: re.Pattern) -> dict:
    """
    匹配html中的初始化json数据，一般适用于那种将初始化json返回的html页面，他们通过json构建dom，爬虫直接提取json
    :param html_content: html内容
    :param pattern: json提取正则表达式，注意将json作为第一个分组， 示例 r'__INITIAL_STATE__=(.+);'
    :return: json字典
    """
    # 返回结果通过js处理成document，只能正则匹配
    search_content = re.search(pattern, html_content)
    if search_content is None:
        log.error('Can not match any data.')
        return {}
    init_json = search_content.group(1)
    try:
        json_data = json.loads(init_json)
        return json_data
    except json.decoder.JSONDecodeError:
        log.error('can not parse json data: {}'.format(init_json))
    return {}


def m_get(data: dict, key: str, default=None):
    """
    用于获取多层级的字典元素
    :param data: dict自动
    :param key: key字符串
    :param default: 默认值
    """
    keys = key.split('.')
    return rget(data, keys, default)


def rget(data, keys, default=None):
    """
    递归获取dict数据
    """
    key = keys.pop(0)
    try:
        elem = data[key]
    except KeyError:
        return default
    except TypeError:
        log.error('The data is not dict.')
        return None
    if not keys:
        return elem
    return rget(elem, keys, default)
