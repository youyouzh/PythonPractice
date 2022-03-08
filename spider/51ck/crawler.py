import re
import time
from typing import List

import shutil
import os
import json

from bs4 import BeautifulSoup

import u_base.u_file as u_file
import u_base.u_log as log
from Crypto.Cipher import AES  # pip install pycryptodome
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'https': 'http://127.0.0.1:1080',
    # },
}


def get_ts_save_dir(m3u8_url: str):
    parse_url = urlparse(urljoin(m3u8_url, ''))
    url_path = os.path.dirname(parse_url.path)
    save_dir = os.path.join(r'result\ts', u_file.convert_windows_path(url_path))
    u_file.ready_dir(save_dir, True)
    return save_dir


def crawl_video_info(template_page_url: str):
    max_page = 140
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
        u_file.cache_json(video_infos, r'result\video-infos.jon')
    return video_infos


def extract_m3u8_url(html_content: str) -> str or None:
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


def extract_title(html_content: str):
    pattern = re.compile(r'content="([^<>]+)剧情:"')
    search_content = re.search(pattern, html_content)
    if search_content is None:
        log.error('Can not match any title.')
        return None
    return search_content.group(1).strip()


def extract_ts_urls(m3u8_url: str) -> List[str]:
    # m3u8 cache file path
    parse_url = urlparse(m3u8_url)
    cache_file = os.path.join(r'result\m3u8', u_file.convert_windows_path(parse_url.path))

    # extract full ts file urls
    response = u_file.get_content_with_cache(m3u8_url, cache_file, **_REQUESTS_KWARGS)
    if response[0:1] == '[':
        ts_urls = json.loads(response)
    else:
        lines = response.split('\n')
        ts_urls: List[str] = [urljoin(m3u8_url, line.rstrip()) for line in lines if line.rstrip().endswith('.ts')]
    if len(ts_urls) == 0:
        log.error('extract ts urls failed.')
        return []

    log.info('total ts urls size: {}'.format(len(ts_urls)))
    return ts_urls


def download_ts_file(m3u8_url: str, ts_urls: List[str]):
    save_dir = get_ts_save_dir(m3u8_url)
    index = 1
    for ts_url in ts_urls:
        file_name = u_file.get_file_name_from_url(ts_url)
        u_file.download_file(ts_url, file_name, save_dir, **_REQUESTS_KWARGS)
        log.info('download ts file success({}/{}): {}'.format(index, len(ts_urls), ts_url))
        index += 1


def download_ts_file_with_pool(m3u8_url: str, ts_urls: List[str]):
    save_dir = get_ts_save_dir(m3u8_url)
    log.info('download ts file with pool.')
    pool = ThreadPoolExecutor(10)
    tasks = []
    for ts_url in ts_urls:
        file_name = u_file.get_file_name_from_url(ts_url)
        future = pool.submit(u_file.download_file, ts_url, file_name, save_dir, **_REQUESTS_KWARGS)
        tasks.append(future)

    wait(tasks, return_when=ALL_COMPLETED)
    log.info('all ts file download success.')


def merge_ts_file(m3u8_url: str, video_name: str, decrypt_function=None):
    merge_file_path = os.path.join(r'result\video', video_name + '.mp4')
    u_file.ready_dir(merge_file_path)
    merge_file_handle = open(merge_file_path, 'wb')

    ts_dir = get_ts_save_dir(m3u8_url)
    for ts_filename in os.listdir(ts_dir):
        if not ts_filename.rstrip().endswith('.ts'):
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
    下载 hsck.us
    :param page_url: 视频页面地址
    :return: None
    """
    response = u_file.get_content(page_url)
    m3u8_url = extract_m3u8_url(response)
    title = extract_title(response)
    download_with_m3u8_url(title, m3u8_url)


def download_with_m3u8_url(title, m3u8_url):
    ts_urls = extract_ts_urls(m3u8_url)
    download_ts_file_with_pool(m3u8_url, ts_urls)
    merge_ts_file(m3u8_url, title)


def decrypt_aes(m3u8_url: str, encrypt_data):
    # get decrypt key
    key_url = urljoin(m3u8_url, 'key.key')
    parse_url = urlparse(key_url)
    cache_file = os.path.join(r'result\m3u8', u_file.convert_windows_path(parse_url.path))
    key = u_file.get_content_with_cache(key_url, cache_file)
    log.info('get key success: {}'.format(key))

    # aes decrypt input
    iv = b'0000000000000000'
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    decrypt_data = cipher.decrypt(encrypt_data)
    return decrypt_data.rstrip(b'\0')


def download_by_m3u8(m3u8_url: str, video_name: str):
    ts_urls = extract_ts_urls(m3u8_url)
    download_ts_file_with_pool(m3u8_url, ts_urls)
    merge_ts_file(m3u8_url, video_name, decrypt_aes)


if __name__ == '__main__':
    # download_by_page_url('http://823ck.cc/vodplay/1649-1-1.html')
    download_with_m3u8_url('xx', 'https://ckcdnz1.cdn2020.com/video/m3u8/2020/06/07/ce331a28/index.m3u8')
    # decrypt_aes()
