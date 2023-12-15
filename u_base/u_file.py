#!/usr/bin/python
# -*- coding: utf-8 -*
# file function


import os
import subprocess
import time
import json
import re
import hashlib
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
    file_name = file_name.split('?')[0]
    return urllib.parse.unquote(file_name)


def covert_url_to_filename(url, with_domain=True, with_path=True, with_query=False, with_md5=False):
    """
    将url转化为文件名，一帮用于缓存文件生成
    :param with_domain: 文件名加上域名
    :param with_path: 文件名加上请求路径
    :param with_query: 文件名加上查询参数
    :param with_md5: 对url使用md5
    :param url: url
    :return: filename
    """
    # 直接对整个url进行md5
    if with_md5:
        return hashlib.md5(url.encode(encoding='utf-8')).hexdigest()

    parse_result = urllib.parse.urlsplit(url)
    file_name = ''
    if with_domain:
        file_name += parse_result.netloc
    if with_path:
        file_name += parse_result.path
    if with_query:
        file_name += parse_result.query
    file_name = convert_windows_path(file_name)
    file_name = file_name[:255]
    return file_name


def get_abs_cache_path():
    """
    获取cache文件夹的绝对路径，方便缓存文件
    :return:
    """
    return os.path.join(os.getcwd(), 'cache')


def ready_dir(file_path: str, is_dir=False):
    """
    准备相关文件夹，检查path所在文件夹是否存在，若不存在则创建
    :param is_dir: 是否是文件夹
    :param file_path: 文件路径，如果是文件夹路径则is_dir=True
    :return: None
    """
    dir_path = file_path if is_dir else os.path.dirname(file_path)
    if not dir_path:
        log.info('The dir path is empty.')
        return
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
    if html_content and use_cache:
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

        response = requests.get(path, **kwargs)
        if encoding is not None and not kwargs.get('stream', None):
            response.encoding = encoding

        log.info('end get info from web url: ' + path)
        if response.status_code != 200:
            log.error('The response status is invalid. code: {}, content: {}'.format(response.status_code, response.content))
            response.raise_for_status()
            return False
        if kwargs.get('stream', None):
            # stream二进制类型
            return response.content
        if response.text is None or response.text == '':
            log.error('The response text is empty.')
        # 处理网页请求编码乱码问题，使用网页中的编码而不是header编码
        response.encoding = response.apparent_encoding
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
        response = requests.get(url, params=params, headers=default_headers, verify=False, **kwargs)
    except Exception as e:
        log.warn('request error and try again. {}'.format(e))
        response = requests.get(url, params=params, headers=default_headers, verify=False, **kwargs)
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


def download_file(url, filename, path=os.path.curdir, replace=False, with_progress=False, **kwargs):
    """
    download file from url
    :param url: image_url
    :param path: save directory path
    :param filename: image name
    :param replace: replace the same name file.
    :param with_progress: with progress when download file.
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
        if 'headers' not in kwargs:
            kwargs['headers'] = COMMON_HEADERS
        else:
            kwargs['headers']['user-agent'] = COMMON_USER_AGENT
        response = requests.get(url, stream=True, **kwargs)
        if response.status_code != 200:
            log.error('download file fail. code: {}, url: {}, '.format(response.status_code, url))
            return False
        if with_progress:
            # 带进度打印日志，控制台可以使用 tqdm 包实现
            with open(file_path, 'ab') as out_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        out_file.write(chunk)
                        log.info('download 1034 success.')
        else:
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


def dump_json_to_file(json_file: str, json_data):
    """
    将json数据存入文件中
    :param json_file:
    :param json_data:
    :return:
    """
    ready_dir(json_file)
    with open(json_file, 'w', encoding='utf-8') as file_handle:
        log.info('dump json to file success. file: {}'.format(json_file))
        json.dump(json_data, file_handle, ensure_ascii=False, indent=4)


def load_json_from_file(json_file: str):
    """
    从文件中加载json数据
    :param json_file:
    :return:
    """
    with open(json_file, 'r', encoding='utf-8') as file_handle:
        log.info('load json from file success. file: {}'.format(json_file))
        return json.load(file_handle)


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
    用于获取多层级的字典元素，例如 m_get(obj, 'user.name')
    :param data: dict自动
    :param key: key字符串
    :param default: 获取不到时的默认值，默认为None
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
        log.warn('The data is not dict: {}'.format(data))
        return None
    if not keys:
        return elem
    return rget(elem, keys, default)


def get_path(file_name: str, with_file_name=True) -> str:
    """
    从完整文件名称获取文件夹
    :param file_name: 文件名称（绝对文件路径）
    :param with_file_name: 是否包含文件名
    :return: 文件路径
    """
    path, file = os.path.split(file_name)
    filename, suffix = os.path.splitext(file)
    return path + filename if with_file_name else ''


def get_file_meta(file_name: str) -> dict:
    """
    提取文件元数据信息
    :param file_name: 文件路径
    :return: 包括文件后缀，路径等的字典
    """
    path, file = os.path.split(file_name)
    filename, suffix = os.path.splitext(file)
    return {
        'path': path,
        'file': file,
        'filename': filename,
        'suffix': suffix
    }


def copy_file_with_replacer(source_path, target_path, content_replacer, delete_source=False) -> bool:
    """
    将文件进行拷贝，同时替换文件内容
    :param source_path: 原始文件路径
    :param target_path: 拷贝文件路径
    :param content_replacer: 内容替换函数
    :param delete_source: 删除原文件
    :return: bool: true表示成功处理
    """
    if not os.path.isfile(source_path):
        log.warn('The file is not exist: '.format(source_path))
        return False
    ready_dir(target_path)
    with open(source_path, 'r+', encoding='utf-8') as file_handle:
        content = file_handle.read()
        content = content_replacer(content)
        if source_path == target_path:
            # 同一个文件，只处理替换，并不删除
            file_handle.seek(0)
            file_handle.write(content)
            return True
        with open(target_path, 'w', encoding='utf-8') as out_handle:
            out_handle.write(content)
    if delete_source:
        os.remove(source_path)


def escape_argument(arg):
    # Escape the argument for the cmd.exe shell.
    # See https://learn.microsoft.com/en-us/archive/blogs/twistylittlepassagesallalike/everyone-quotes-command-line-arguments-the-wrong-way
    #
    # First we escape the quote chars to produce a argument suitable for
    # CommandLineToArgvW. We don't need to do this for simple arguments.

    if not arg or re.search(r'(["\s])', arg):
        arg = '"' + arg.replace('"', r'\"') + '"'

    return escape_for_cmd_exe(arg)


def escape_for_cmd_exe(arg):
    # Escape an argument string to be suitable to be passed to
    # cmd.exe on Windows
    #
    # This method takes an argument that is expected to already be properly
    # escaped for the receiving program to be parsed by it. This argument
    # will be further escaped to pass the interpolation performed by cmd.exe
    # unchanged.
    #
    # Any meta-characters will be escaped, removing the ability to e.g. use
    # redirects or variables.
    #
    # @param arg [String] a single command line argument to escape for cmd.exe
    # @return [String] an escaped string suitable to be passed as a program
    #   argument to cmd.exe
    meta_re = re.compile(r'([()%!^"<>&|])')
    return meta_re.sub('^\1', arg)


def run_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in process.stdout:
        line = line.rstrip().decode('utf-8')
        print(">>>", line)
