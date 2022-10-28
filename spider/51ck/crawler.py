import re
import shutil
import os
import json

from typing import List
from bs4 import BeautifulSoup

import u_base.u_file as u_file
import u_base.u_log as log
from Crypto.Cipher import AES  # pip install pycryptodome
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'https': 'http://127.0.0.1:1080',  # use proxy
    # },
    # 'verify': False,

    # 下面的header适用于 https://www.xvideos.com/
    # 'verify': False,  # 必须关闭
    'headers': {
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site'
    }
}
POOL_SIZE = 10


def get_ts_save_dir(m3u8_url: str):
    """
    根据资源路径生成保存文件夹路径
    :param m3u8_url: m3u8 url
    :return: 保存文件夹名
    """
    save_dir = os.path.join(r'result\ts', u_file.get_md5_file_name_from_url(m3u8_url))
    u_file.ready_dir(save_dir, True)
    return save_dir


def crawl_video_info(template_page_url: str):
    """
    爬取网页视频信息，分页爬取，主要有标题，观看数，喜欢数，下载地址
    :param template_page_url: 首页url
    :return:
    """
    max_page = 263
    video_infos = []
    parse_url = urlparse(template_page_url)
    for index in range(1, max_page):
        log.info('begin crawl page.({}/{})'.format(index, max_page))
        html_content = u_file.get_content(template_page_url.format(index))
        soup = BeautifulSoup(html_content, 'lxml')

        video_nodes = soup.select('div.stui-vodlist__detail')
        log.info('video size: {}'.format(len(video_nodes)))
        for video_node in video_nodes:
            a_node = video_node.select_one('h4 > a')
            span_node = video_node.select('p.sub > span')
            view_count = int(span_node[2].text.strip())
            like_count = int(span_node[1].text.strip())
            video_infos.append({
                'title': a_node.string,
                'url': parse_url._replace(path=a_node['href']).geturl(),
                'view': view_count,
                'like': like_count
            })
        video_infos.sort(key=lambda x: x['like'], reverse=True)
        u_file.cache_json(video_infos, r'result\video-infos-zh.json')
    return video_infos


def extract_m3u8_url(html_content: str) -> str or None:
    """
    从网页中提取视频流 m3u8 下载地址
    :param html_content: html页面内容
    :return:
    """
    # 正在匹配查找资源
    pattern = re.compile(r'player_aaaa=(\{.+\})')
    search_content = re.search(pattern, html_content)
    if search_content is None:
        log.error('Can not match any m3u8 url.')
        exit(0)
        return None
    init_json = search_content.group(1)
    json_data = json.loads(init_json)
    if 'url' not in json_data:
        log.error('Can not find url: {}'.format(init_json))
        return None
    log.info('extract url: {}'.format(json_data['url']))
    return json_data['url']


def extract_ts_urls(m3u8_url: str) -> List[str]:
    """
    查询m3u8_url，获取所有视频片段ts的下载地址
    :param m3u8_url: m3u8视频流地址
    :return: ts下载地址列表
    """
    # m3u8 cache file path
    cache_file = os.path.join(r'result\m3u8', u_file.get_md5_file_name_from_url(m3u8_url))

    # extract full ts file urls
    response = u_file.get_content_with_cache(m3u8_url, cache_file, **_REQUESTS_KWARGS)
    if response[0:1] == '[':
        ts_urls = json.loads(response)
    else:
        lines = response.split('\n')
        ts_urls: List[str] = [urljoin(m3u8_url, line.rstrip()) for line in lines if '.ts' in line.rstrip()]
    if len(ts_urls) == 0:
        log.error('extract ts urls failed.')
        return []

    log.info('total ts urls size: {}'.format(len(ts_urls)))
    return ts_urls


def download_ts_file_with_pool(m3u8_url: str, ts_urls: List[str]):
    """
    多线程线程池下载视频分片ts文件
    :param m3u8_url:
    :param ts_urls:
    :return:
    """
    save_dir = get_ts_save_dir(m3u8_url)
    log.info('download ts file with pool.')
    pool = ThreadPoolExecutor(POOL_SIZE)
    tasks = []
    for ts_url in ts_urls:
        file_name = u_file.get_file_name_from_url(ts_url)
        future = pool.submit(u_file.download_file, ts_url, file_name, save_dir, **_REQUESTS_KWARGS)
        tasks.append(future)

    # 等待所有线程完成
    wait(tasks, return_when=ALL_COMPLETED)
    log.info('all ts file download success.')


def merge_ts_file(m3u8_url: str, video_name: str, decrypt_function=None):
    """
    合并视频分片ts文件
    :param m3u8_url: 视频流地址
    :param video_name: 视频名称
    :param decrypt_function: ts文件解密算法
    :return:
    """
    merge_file_path = os.path.join(r'result\video', video_name + '.mp4')
    u_file.ready_dir(merge_file_path)
    merge_file_handle = open(merge_file_path, 'wb')

    ts_dir = get_ts_save_dir(m3u8_url)
    for ts_filename in os.listdir(ts_dir):
        if '.ts' not in ts_filename.rstrip():
            continue
        ts_filepath = os.path.join(ts_dir, ts_filename)
        ts_file_handle = open(ts_filepath, 'rb')
        ts_file_content = ts_file_handle.read()
        if decrypt_function is not None:
            # if defined decrypt function, decrypt the data
            ts_file_content = decrypt_function(m3u8_url, ts_file_content)
        shutil.copyfileobj(ts_file_handle, merge_file_handle)
        merge_file_handle.write(ts_file_content)
        ts_file_handle.close()
    merge_file_handle.close()
    log.info('merge file success: {}'.format(merge_file_path))


def download_by_page_url(page_url: str):
    """
    下载 hscangku.com 指定页面视频
    :param page_url: 视频页面地址
    :return: None
    """
    response = u_file.get_content(page_url)
    m3u8_url = extract_m3u8_url(response)

    # 正则匹配提取视频标题
    pattern = re.compile(r'content="([^<>]+)剧情:"')
    search_content = re.search(pattern, response)
    title = search_content.group(1).strip()

    download_with_m3u8_url(title, m3u8_url)


def download_with_m3u8_url(title, m3u8_url, decrypt_function=None):
    """
    下载m3u8视频
    :param title: 视频标题，用于保存文件名
    :param m3u8_url: m3u8视频地址
    :param decrypt_function: 如果视频流有加密，需要提供解密算法
    """
    ts_urls = extract_ts_urls(m3u8_url)
    download_ts_file_with_pool(m3u8_url, ts_urls)
    merge_ts_file(m3u8_url, title, decrypt_function)


def decrypt_aes(m3u8_url: str, encrypt_data):
    """
    视频流AES解密算法实现
    :param m3u8_url: 视频流地址，获取解密key
    :param encrypt_data: 加密数据
    :return:
    """
    # get decrypt key
    key_url = urljoin(m3u8_url, 'key.key')
    cache_file = os.path.join(r'result\m3u8', u_file.get_md5_file_name_from_url(m3u8_url))
    key = u_file.get_content_with_cache(key_url, cache_file)
    log.info('get key success: {}'.format(key))

    # aes decrypt input
    iv = b'0000000000000000'
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    decrypt_data = cipher.decrypt(encrypt_data)
    return decrypt_data.rstrip(b'\0')


if __name__ == '__main__':
    download_by_page_url('http://645ck.cc/vodplay/16553-1-1.html')
    # crawl_video_info('http://666386.xyz/vodtype/15-{}.html')
    # decrypt_aes()
