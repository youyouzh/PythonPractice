import re
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
    'proxies': {
      'https': 'http://127.0.0.1:1080',
    },
}


def get_ts_ave_dir(m3u8_url: str):
    parse_url = urlparse(urljoin(m3u8_url, ''))
    url_path = os.path.dirname(parse_url.path)
    save_dir = os.path.join(r'result', u_file.convert_windows_path(url_path))
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
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
    response = u_file.get_content(m3u8_url, **_REQUESTS_KWARGS)
    parse_url = urlparse(m3u8_url)
    cache_file = u_file.convert_windows_path(parse_url.path)
    cache_file = os.path.join(r'result', cache_file)
    if os.path.isfile(cache_file):
        return u_file.load_json_from_file(cache_file)

    lines = response.split('\n')
    ts_urls: List[str] = [urljoin(m3u8_url, line.rstrip()) for line in lines if line.rstrip().endswith('.ts')]
    if len(ts_urls) == 0:
        log.error('extract ts urls failed.')
        return []

    log.info('total ts urls size: {}'.format(len(ts_urls)))
    u_file.cache_json(ts_urls, cache_file)
    return ts_urls


def download_ts_file(m3u8_url: str, ts_urls: List[str]):
    save_dir = get_ts_ave_dir(m3u8_url)
    index = 1
    for ts_url in ts_urls:
        file_name = u_file.get_file_name_from_url(ts_url)
        u_file.download_file(ts_url, file_name, save_dir, **_REQUESTS_KWARGS)
        log.info('download ts file success({}/{}): {}'.format(index, len(ts_urls), ts_url))
        index += 1


def download_ts_file_with_pool(m3u8_url: str, ts_urls: List[str]):
    pool = ThreadPoolExecutor(10)
    save_dir = get_ts_ave_dir(m3u8_url)
    tasks = []
    for ts_url in ts_urls:
        file_name = u_file.get_file_name_from_url(ts_url)
        future = pool.submit(u_file.download_file, ts_url, file_name, save_dir, **_REQUESTS_KWARGS)
        tasks.append(future)

    wait(tasks, return_when=ALL_COMPLETED)
    log.info('all ts file download success.')


def merge_ts_file(m3u8_url: str, video_name: str):
    merge_file_path = os.path.join(r'result', video_name)
    merge_file_handle = open(merge_file_path, 'wb')

    ts_dir = get_ts_ave_dir(m3u8_url)
    for ts_filename in os.listdir(ts_dir):
        if not ts_filename.rstrip().endswith('.ts'):
            continue
        ts_filepath = os.path.join(ts_dir, ts_filename)
        ts_file_handle = open(ts_filepath, 'rb')
        shutil.copyfileobj(ts_file_handle, merge_file_handle)
        ts_file_handle.close()
    merge_file_handle.close()
    log.info('merge file success: {}'.format(merge_file_path))


def download_video(page_url: str):
    response = u_file.get_content(page_url)
    m3u8_url = extract_m3u8_url(response)
    title = extract_title(response)
    ts_urls = extract_ts_urls(m3u8_url)
    download_ts_file_with_pool(m3u8_url, ts_urls)
    merge_ts_file(m3u8_url, title + '.mp4')

def get_asc_key(key):
    '''
    获取密钥，把16进制字节码转换成ascii码
    :param key:从网页源代码中获取的16进制字节码
    :return: ascii码格式的key
    '''
    # 最简洁的写法
    # asc_key = [chr(int(i,16)) for i in key.split(',')]
    # 通俗易懂的写法
    key = key.split(',')
    asc_key = ''
    for i in key:
        i = int(i, 16)  # 16进制转换成10进制
        i = chr(i)  # 10进制转换成ascii码
        asc_key += i
    return asc_key


def decrypt_aes_128():
    iv = b'0000000000000000'
    key = '21464093fdd9cef9'
    decrypt_file_handler = open(r'result\yu-3-aes-128-key-21464093fdd9cef9.mp4', 'rb')
    output_file_handler = open(r'result\yu-3.mp4', 'wb')
    part = decrypt_file_handler.read()
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    plain_data = cipher.decrypt(part)
    if part:
        output_file_handler.write(plain_data)


def download_by_m3u8():
    m3u8_url = 'https://c32.cdn.dycp444.com/202107/19/EOqUqAYi/500kb/hls/index.m3u8?sign=Q7euXu3gu8cqCPdjOyiyDA&t=1628280091'
    ts_urls = extract_ts_urls(m3u8_url)
    download_ts_file_with_pool(m3u8_url, ts_urls)
    merge_ts_file(m3u8_url, 'yu-1-aes-128-key-7bdf6a0bc9daaffd.mp4')


if __name__ == '__main__':
    url = 'http://51ck.cc/vodplay/3685-1-1.html'
    # download_video(url)
    # download_by_m3u8()
    decrypt_aes_128()
