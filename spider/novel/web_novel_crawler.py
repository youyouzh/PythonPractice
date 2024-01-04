"""
小说爬虫
"""
import re

from bs4 import BeautifulSoup

import u_base.u_file as u_file
import u_base.u_log as log

_REQUESTS_KWARGS = {
    # 'proxies': {
    #   'socks': 'http://127.0.0.1:1080',  # use proxy
    # },
    # 'verify': False,

    # 下面的header适用于 https://www.xvideos.com/
    # 'verify': False,  # 必须关闭
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site'
    },
    'retry': 2,
    'timeout': (2, 3),   # 设置连接超时时间为2秒，读取超时时间为3秒
}


SELECTOR_MAP = {
    'b.faloo.com': {
        'home_url': 'https://b.faloo.com',
        'chapter_url': 'div.c_con_list > div.c_con_li_detail_p > a',
        'chapter_content': 'div.noveContent'
    },
    'book.sfacg.com': {
        'home_url': 'https://book.sfacg.com/',
        'chapter_url': 'div.catalog-list > ul > li > a',
        'chapter_content': 'div.article-content > p'
    }
}


def crawl_chapter_urls(chapter_index_url: str, selector_tag: str) -> list:
    """
    爬取章节目录
    :param chapter_index_url: 章节目录页面地址
    :param selector_tag: 选择器
    :return: 章节列表
    """
    html_content = u_file.get_content_with_cache(chapter_index_url, **_REQUESTS_KWARGS)
    soup = BeautifulSoup(html_content, 'lxml')

    chapter_url_nodes = soup.select(SELECTOR_MAP[selector_tag]['chapter_url'])
    log.info('crawl chapter html content finish. chapter url sizes: {}'.format(len(chapter_url_nodes)))

    chapter_urls = []
    for chapter_url_node in chapter_url_nodes:
        if not chapter_url_node or '#' == chapter_url_node['href']:
            log.warn('skip empty chapter url: {}'.format(chapter_url_node))
            continue
        full_url = chapter_url_node['href']
        if full_url.startswith('http'):
            pass
        elif full_url.startswith('//'):
            # 处理缩写链接
            full_url = 'https:' + full_url
        else:
            # 处理以缩写域名
            full_url = 'https://' + selector_tag + full_url
        chapter_index_url = {
            'title': chapter_url_node['title'],
            'url': full_url
        }
        chapter_urls.append(chapter_index_url)

    log.info('crawl chapter url finish. size: {}'.format(len(chapter_urls)))

    # 处理分页章节爬取
    return chapter_urls


def crawl_chapter_content(chapter_url: str, selector_tag: str) -> str:
    """
    获取章节内容
    :param chapter_url: 章节内容url
    :param selector_tag: 选择器
    :return: 章节内容
    """
    chapter_content = u_file.get_content_with_cache(chapter_url, **_REQUESTS_KWARGS)
    chapter_soup = BeautifulSoup(chapter_content, 'lxml')
    chapter_content_p_nodes = chapter_soup.select(SELECTOR_MAP[selector_tag]['chapter_content'])
    if not chapter_content_p_nodes:
        log.error('get chapter content empty. chapter_url: {}'.format(chapter_url))
        return ''
    chapter_content = ''
    for chapter_content_p_node in chapter_content_p_nodes:
        chapter_content += chapter_content_p_node.text.strip() + '\n'
    return chapter_content


def crawl_content(chapter_index_url: str, novel_title: str):
    """
    爬取小说内容
    :param chapter_index_url:  章节目录页面地址
    :param novel_title: 小说标题
    :return:
    """
    selector_tag_regex = re.compile('//([^/]+)/')
    selector_tag_result = selector_tag_regex.search(chapter_index_url)
    if not selector_tag_result or not selector_tag_result.groups():
        log.error('can not match selector tag: {}'.format(chapter_index_url))
        return False
    selector_tag = selector_tag_result.groups()[0]
    log.info('match selector tag: {}'.format(selector_tag))
    chapter_urls = crawl_chapter_urls(chapter_index_url, selector_tag)
    novel_content = ''
    novel_save_path = f'result\\{novel_title}.txt'

    for chapter_url in chapter_urls:
        log.info('----> begin crawl chapter: {}'.format(chapter_url))
        novel_content += '\n\n' + chapter_url['title'] + '\n\n'
        chapter_content = crawl_chapter_content(chapter_url['url'], selector_tag)
        if not chapter_content or len(chapter_content) <= 100:
            log.error('chapter content is less. chapter_url: {}, content: {}'.format(chapter_url, chapter_content))
            continue
        novel_content += chapter_content
        u_file.write_content(novel_save_path, novel_content)


def crawler_from_shuba(novel_index_page_url, novel_title: str):
    """
    支持从 https://www.69shuba.com 爬取内容
    :param novel_index_page_url: 小说章节目录页
    :param novel_title: 小说书名
    :return:
    """
    html_content = u_file.get_content_with_cache(novel_index_page_url, **_REQUESTS_KWARGS)
    soup = BeautifulSoup(html_content, 'lxml')

    chapter_menu_nodes = soup.select('div.catalog > ul > li > a')
    log.info('chapter size: {}'.format(chapter_menu_nodes))
    novel_content = ''
    for chapter_menu_node in chapter_menu_nodes:
        # 跳过空链接
        chapter_content_url = chapter_menu_node['href']
        if not chapter_content_url or '#' == chapter_content_url:
            log.warn('skip empty url: {}'.format(chapter_menu_node))
            continue

        log.info('begin crawler content from chapter: {}'.format(chapter_menu_node))
        chapter_content = u_file.get_content_with_cache(chapter_menu_node['href'], **_REQUESTS_KWARGS)
        chapter_soup = BeautifulSoup(chapter_content, 'lxml')
        chapter_content_node = chapter_soup.select('div.txtnav')
        if not chapter_content_node:
            log.error('get chapter content empty. {}'.format(chapter_menu_node))
            continue
        chapter_content_node = chapter_content_node[0]
        novel_content += chapter_content_node.text + '\n'
    novel_save_path = f'cache\\{novel_title}.txt'
    u_file.write_content(novel_save_path, novel_content)
    return novel_save_path


if __name__ == '__main__':
    crawl_content('https://book.sfacg.com/Novel/552847/MainIndex/', '病娇徒儿对天生媚骨的我图谋不轨')
