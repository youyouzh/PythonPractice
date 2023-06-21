import re
import os
import json


from Crypto.Util.Padding import pad
from bs4 import BeautifulSoup

import u_base.u_file as u_file
import u_base.u_log as log
from m3u8_video_crawler import download_with_m3u8_url
from Crypto.Cipher import AES  # pip install pycryptodome
from urllib.parse import urlparse, urljoin

_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'socks': 'http://127.0.0.1:1080',  # use proxy
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
MEMORY_CACHE = {}   # 全局内存缓存


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


def decrypt_aes(m3u8_url: str, encrypt_data):
    """
    视频流AES解密算法实现
    :param m3u8_url: 视频流地址，获取解密key
    :param encrypt_data: 加密数据
    :return:
    """
    # get decrypt key
    if 'hls/index.m3u8' in m3u8_url:
        # https://www.pornlulu.com/ 网站key路径取法
        key_url = m3u8_url.replace('index.m3u8', 'key.key')
    else:
        key_url = urljoin(m3u8_url, 'key.key')

    # 获取key
    if 'aes-key' in MEMORY_CACHE:
        key = MEMORY_CACHE['aes-key']
    else:
        cache_file = os.path.join(r'result\m3u8', u_file.covert_url_to_filename(key_url))
        key = u_file.get_content_with_cache(key_url, cache_file)
        MEMORY_CACHE['aes-key'] = key
        log.info('get key success: {}'.format(key))

    # aes decrypt input
    iv = b'0000000000000000'
    cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
    decrypt_data = cipher.decrypt(encrypt_data)
    return decrypt_data.rstrip(b'\0')


def decrypt_aes_jable_tv(m3u8_url: str, encrypt_data):
    # jable.tv 解密
    if 'aes-key' not in MEMORY_CACHE:
        # 缓存数据，避免每次都调用
        cache_file = os.path.join(r'result\m3u8', u_file.covert_url_to_filename(m3u8_url))
        response = u_file.get_content_with_cache(m3u8_url, cache_file, **_REQUESTS_KWARGS)
        decrypt_content_regex = re.compile(r'EXT-X-KEY:METHOD=AES-128,URI="(\w+.ts)",IV=0x(\w+)')
        search_result = decrypt_content_regex.search(response)
        if not search_result or not search_result.groups():
            log.error('can not fin decrypt content from response.')
            return
        decrypt_key_url = urljoin(m3u8_url, search_result.groups()[0])
        key = u_file.get_content_with_cache(decrypt_key_url, stream=True, use_cache=False)
        # key = b'\x07\xe3\x17]\xddW|\xa1\xe2f&\x91+\xf6\x82\xfc'
        # iv = hex(int(search_result.groups()[1], 16))
        iv = search_result.groups()[1]
        iv = bytes.fromhex(iv)
        MEMORY_CACHE['aes-key'] = key
        MEMORY_CACHE['aes-iv'] = iv
    else:
        key = MEMORY_CACHE.get('aes-key')
        iv = MEMORY_CACHE.get('aes-iv')

    cipher = AES.new(key, AES.MODE_CBC, iv)
    if len(encrypt_data) % 16 != 0:
        # Data must be padded to 16 byte boundary in CBC mode
        # 长度填充
        encrypt_data = pad(encrypt_data, 16)
    decrypt_data = cipher.decrypt(encrypt_data)

    return decrypt_data.rstrip(b'\0')


def try_decrypt_ts_file():
    ts_filepath = r'G:\Projects\Python_Projects\python-base\spider\51ck\result\ts\hoyo-toba.mushroomtrack.com-hls-_nhTPd395KOq9XLnwJ8mFQ-1686335938-18000-18526-18526.m3u8\185261.ts'
    m3u8_url = 'https://hoyo-toba.mushroomtrack.com/hls/_nhTPd395KOq9XLnwJ8mFQ/1686335938/18000/18526/18526.m3u8'
    ts_file_handle = open(ts_filepath, 'rb')
    ts_file_content = ts_file_handle.read()

    decrypt_ts_filepath = r'result\decrypt_ts-2.ts'
    decrypt_ts_handle = open(decrypt_ts_filepath, 'wb')

    decrypt_file_content = decrypt_aes_jable_tv(m3u8_url, ts_file_content)
    decrypt_ts_handle.write(decrypt_file_content)
    ts_file_handle.close()
    decrypt_ts_handle.close()


if __name__ == '__main__':
    # download_by_page_url('http://645ck.cc/vodplay/16553-1-1.html')
    # crawl_video_info('http://666386.xyz/vodtype/15-{}.html')
    try_decrypt_ts_file()
