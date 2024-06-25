import copy
import re
import os
import json

from typing import List

import sys

import requests

sys.path.append(r'D:\work\github\PythonPractice')

import u_base.u_file as u_file
import u_base.u_log as log
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'socks': 'http://127.0.0.1:1080',  # use proxy
    # },
    # 'verify': False,

    # 下面的header适用于 https://www.xvideos.com/
    # 'verify': False,  # 必须关闭
    # https://missav.com/ header 必须包含Referer
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'Origin': 'https://missav.com',  # dynamic set by request url
        'Referer': 'https://missav.com',
        # 'Referer': 'https://javplayer.me/',
        # 'Origin': 'https://javplayer.me/',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site'
    }
}
SUPPORT_TS_TYPES = ['.ts', '.txt', '.jpeg', '.jpg']
DOWNLOAD_THREAD_POOL_SIZE = 8   # 下载线程池数量
REPLACE_SAME_NAME_VIDEO = False   # 替换同名视频
DOWNLOAD_CHUNK_SIZE = 10 * 1024 * 1024
FFMPEG_PATH = r'D:\work\software\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe'
DOWNLOAD_VIDEOS = [
# ('xxx', 'https://ap-drop-monst.mushroomtrack.com/bcdn_token=xxx&token_path=110112.m3u8'),
]


def get_ts_save_dir(m3u8_url: str):
    """
    根据资源路径生成保存文件夹路径
    :param m3u8_url: m3u8 url
    :return: 保存文件夹名
    """
    save_dir = os.path.join(r'result\ts', u_file.covert_url_to_filename(m3u8_url))
    u_file.ready_dir(save_dir, True)
    return save_dir


def get_request_headers(base_url: str):
    headers = copy.deepcopy(_REQUESTS_KWARGS['headers'])
    # set Origin and Refer
    parsed_url = urlparse(base_url)
    headers['Origin'] = parsed_url.scheme + '://' + parsed_url.netloc
    headers['Referer'] = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
    return headers


def get_ts_download_filename(ts_url: str):
    """
    统一获取ts文件下载保存文件名称
    :param ts_url: ts下载地址
    :return: 文件名
    """
    return u_file.get_file_name_from_url(ts_url)


def extract_ts_urls(m3u8_url: str, m3u8_content: str) -> List[str]:
    """
    获取所有视频片段ts的下载地址
    :param m3u8_url: m3u8视频地址，用于拼接完整的ts路径
    :param m3u8_content: m3u8视频数据
    :return: ts下载地址列表
    """
    # extract full ts file urls
    if m3u8_content.startswith('['):
        # json格式的地址列表
        ts_urls = json.loads(m3u8_content)
    elif m3u8_content.startswith('<!DOCTYPE html>'):
        # html 内容，这说明下载失败
        log.error('can not get ts urls. return html doc.')
        return []
    else:
        lines = m3u8_content.split('\n')
        ts_urls: List[str] = []
        for line in lines:
            for ts_type in SUPPORT_TS_TYPES:
                if ts_type in line:
                    ts_urls.append(urljoin(m3u8_url, line.rstrip()))
    if len(ts_urls) == 0:
        log.error('extract ts urls failed.')
        return []

    log.info('total ts urls size: {}'.format(len(ts_urls)))
    return ts_urls


def get_not_finish_ts_urls(ts_urls: List[str], save_dir: str) -> List[str]:
    """
    技术按指定文件夹下没有下完的ts_urls
    :param ts_urls: ts文件下载地址列表
    :param save_dir: 保存路径
    :return: 没有下载的ts文件下载地址列表
    """
    not_finished_ts_urls = []
    for ts_url in ts_urls:
        filename = u_file.get_file_name_from_url(ts_url)
        filepath = os.path.join(save_dir, filename)
        if not os.path.isfile(filepath):
            not_finished_ts_urls.append(ts_url)
    return not_finished_ts_urls


def download_ts_file_with_pool(ts_urls: List[str], save_dir, retry_count=10):
    """
    多线程线程池下载视频分片ts文件
    :param ts_urls: ts视频片段地址列表
    :param save_dir: ts视频片段保存地址
    :param retry_count: 重试次数
    :return:
    """
    log.info('download ts file with pool. ts file size: {}'.format(len(ts_urls)))
    pool = ThreadPoolExecutor(DOWNLOAD_THREAD_POOL_SIZE)
    tasks = []
    for ts_url in ts_urls:
        filename = u_file.get_file_name_from_url(ts_url)
        future = pool.submit(u_file.download_file, ts_url, filename, save_dir, **_REQUESTS_KWARGS)
        tasks.append(future)

    # 等待所有线程完成
    wait(tasks, return_when=ALL_COMPLETED)

    # 检查是否所有文件都下载完成，并记录未完成下载的ts_url
    not_finished_ts_urls = get_not_finish_ts_urls(ts_urls, save_dir)

    # 递归下载未完成的ts_url
    if retry_count >= 0 and not_finished_ts_urls:
        log.info('not finished ts_urls size: {}, retry times: {}'.format(len(not_finished_ts_urls), retry_count))
        download_ts_file_with_pool(not_finished_ts_urls, save_dir, retry_count - 1)

    not_finished_ts_urls = get_not_finish_ts_urls(ts_urls, save_dir)
    if not_finished_ts_urls:
        # 存在部分ts文件没下载成功则结束，不进行合并
        log.error('some ts file is download fail. size: {}'.format(len(not_finished_ts_urls)))
        return False
    log.info('all ts file download success.')


# javhub.net 下载高清视频
def download_mp4(video_url: str, save_filepath: str):
    response = requests.get(video_url, stream=True, **_REQUESTS_KWARGS)
    if response.status_code != 200:
        log.error('download email fail. code: {}.'.format(response.status_code))
        return False
    log.info('download file save path: {}'.format(save_filepath))

    # 打开文件准备写入
    with open(save_filepath, 'wb') as file_handler:
        # 初始化已下载大小
        downloaded = 0
        print_downloaded = 0  # 记录进度打印时的大小

        # 以1024字节（1MB）的块大小进行读取
        for data in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            if not data:
                continue
            # 更新已下载大小
            downloaded += len(data)

            # 将数据写入文件
            file_handler.write(data)

            # 打印已下载的数据量（例如，每下载1MB打印一次）
            # 将下载进度信息写入文件
            if downloaded - print_downloaded >= DOWNLOAD_CHUNK_SIZE:
                download_size_desc = str(int(downloaded / (1024 * 1024))) + 'MB'
                log.info(f"已下载 {download_size_desc}")
                print_downloaded = downloaded
    log.info('download finished: {}'.format(video_url))
    return True


def download_decrypt_key(m3u8_url: str, m3u8_content: str, key_save_dir: str):
    """
    下载m3u8视频的解密密钥，如果不需要解密，这不用下载
    :param m3u8_url: m3u8视频地址，用于拼接完整的ts路径
    :param m3u8_content: m3u8视频数据
    :param key_save_dir: key文件保存路径
    :return: ts下载地址列表
    """
    decrypt_content_regex = re.compile(r'EXT-X-KEY:METHOD=AES-128,URI="(\w+.ts)",IV=0x(\w+)')
    search_result = decrypt_content_regex.search(m3u8_content)
    if not search_result or not search_result.groups():
        log.warn('Can not find any AES decrypt URI.')
        return
    decrypt_key_filename = search_result.groups()[0]
    decrypt_key_url = urljoin(m3u8_url, search_result.groups()[0])
    u_file.download_file(decrypt_key_url, decrypt_key_filename, key_save_dir, **_REQUESTS_KWARGS)


def merge_ts_file_by_ffmpeg(m3u8_save_path: str, merge_video_path: str):
    """
    使用ffmpeg合并ts文件
        -f concat，-f 一般设置输出文件的格式，如-f psp（输出psp专用格式），但是如果跟concat，则表示采用concat协议，对文件进行连接合并
        -safe 0，用于忽略一些文件名错误，如长路径、空格、非ANSIC字符
        -i xxx.m3u8 后面加输入文件名，也可以输入ts文件名
        -c copy c表示输出文件采用的编码器，后面跟copy，表示直接复制，不重新编码
        -y 自动覆盖文件
    ffmpeg下载地址：
    https://ffmpeg.org/download.html
    https://www.gyan.dev/ffmpeg/builds/
    :param m3u8_save_path: m3u8文件夹路径
    :param merge_video_path: 合并生成视频文件保存路径
    :return:
    """
    m3u8_save_path = os.path.abspath(m3u8_save_path)  # 命令行运行需要完全路径，注意路径中不能又星号*
    merge_command = r'{} -allowed_extensions ALL -y -i "{}" -c copy "{}"'\
        .format(FFMPEG_PATH, m3u8_save_path, merge_video_path).replace('\\', '\\\\')
    log.info('begin merge file by ffmpeg: {}'.format(merge_command))
    u_file.run_command(merge_command)
    log.info('merge file success: {}'.format(merge_video_path))


def download_with_m3u8_url(title, m3u8_url):
    """
    下载m3u8视频
    :param title: 视频标题，用于保存文件名
    :param m3u8_url: m3u8视频地址
    """
    merge_video_filename = title + '.mp4'
    merge_video_path = os.path.join(r'result\video', merge_video_filename)
    merge_video_path = os.path.abspath(merge_video_path)
    u_file.ready_dir(merge_video_path)

    # 检查文件是否已经存在，避免重新下载合并
    if os.path.isfile(merge_video_path):
        log.warn('The same name video file is exist: {}'.format(merge_video_path))
        if not REPLACE_SAME_NAME_VIDEO:
            return False

    save_dir = get_ts_save_dir(m3u8_url)
    m3u8_save_path = os.path.join(save_dir, 'index.m3u8')
    # request get m3u8 file content
    m3u8_content = u_file.get_content_with_cache(m3u8_url, m3u8_save_path, **_REQUESTS_KWARGS)
    if not m3u8_content:
        log.error('get m3u8 content failed: {}'.format(m3u8_url))
        return

    # 从m3u8信息总提取ts下载地址
    ts_urls = extract_ts_urls(m3u8_url, m3u8_content)
    if not ts_urls:
        log.error('extract ts_urls failed: {}'.format(m3u8_url))
        return

    # 使用线程池下载ts文件列表
    download_ts_file_with_pool(ts_urls, save_dir)

    # 下载解密密钥，并将秘钥放到指定目录，用于ffmpeg解密
    download_decrypt_key(m3u8_url, m3u8_content, save_dir)

    # m3u8文件中的ts路径可能有参数，去掉参数，否则会影响ffmpeg合并视频
    process_m3u8_save_path = os.path.join(save_dir, 'index-simple.m3u8')
    meu8_content = u_file.read_content(m3u8_save_path)
    meu8_content = re.sub(r'\.ts\?\S+', '.ts', meu8_content)
    u_file.write_content(process_m3u8_save_path, meu8_content)

    # 使用ffmpeg合并ts文件
    merge_ts_file_by_ffmpeg(process_m3u8_save_path, merge_video_path)


def download_with_mp4_url(title, mp4_url):
    save_video_filename = title + '.mp4'
    log.info('begin download mp4 video finish: {}'.format(title))
    u_file.download_file(mp4_url, save_video_filename, path=r'result\video')
    log.info('download mp4 video finish: {}'.format(title))


if __name__ == '__main__':
    merge_video_path = os.path.join(r'result\video', 'test.mp4')
    merge_video_path = os.path.abspath('test.mp4')
    download_mp4('https://21.2babes.com/mp4/cf5180789578eed165633803e9d3d29e.mp4?md5=sSX9ndcfyz5CrrDmMbDBQQ&expires=1717023719', merge_video_path)
    for (name, url) in DOWNLOAD_VIDEOS:
        download_with_m3u8_url(name, url)
