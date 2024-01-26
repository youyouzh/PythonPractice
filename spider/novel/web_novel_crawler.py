"""
小说爬虫
"""
import json
import re

from urllib.parse import urlparse
from bs4 import BeautifulSoup

import u_base.u_file as u_file
import u_base.u_log as log

REQUESTS_KWARGS = {
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


class CrawlConfig(object):

    def __init__(self,
                 home_url: str,
                 chapter_url_selector: str = '',
                 chapter_title_selector: str = '',
                 chapter_content_selector: str = '',
                 next_chapter_url_selector: str = '',
                 ):
        self.home_url = home_url
        self.domain = urlparse(self.home_url).netloc
        self.chapter_url_selector = chapter_url_selector
        self.chapter_title_selector = chapter_title_selector
        self.chapter_content_selector = chapter_content_selector
        self.next_chapter_url_selector = next_chapter_url_selector


CRAWL_CONFIGS = [
    CrawlConfig(home_url='https://b.faloo.com',
                chapter_url_selector='div.c_con_list > div.c_con_li_detail_p > a',
                chapter_content_selector='div.noveContent > p'
                ),
    CrawlConfig(home_url='https://book.sfacg.com/',
                chapter_url_selector='div.catalog-list > ul > li > a',
                chapter_content_selector='div.article-content > p'
                ),
    CrawlConfig(home_url='https://www.69shuba.com/',
                chapter_url_selector='div.catalog > ul > li > a',
                chapter_content_selector='div.txtnav > p',
                ),
    CrawlConfig(home_url='https://325def1d9a6.12bqg.com/',
                chapter_title_selector='span.title',
                chapter_content_selector='div#chaptercontent',
                next_chapter_url_selector='a#pb_next'
                ),
    CrawlConfig(home_url='https://ncode.syosetu.com/',
                chapter_title_selector='p.novel_subtitle',
                chapter_content_selector='div#novel_honbun',
                next_chapter_url_selector='a.novelview_pager-next'
                ),
]


def get_crawl_config(source_url: str) -> CrawlConfig:
    for crawl_config in CRAWL_CONFIGS:
        if crawl_config.domain == urlparse(source_url).netloc:
            return crawl_config
    log.error('can not find the crawl config for url: {}'.format(source_url))
    raise Exception('can not find crawl config')


def patch_url(source_url: str, extract_url: str) -> str:
    """
    补全URL，很多页面元素中提取的URL可能不包含host等，进行统一处理
    :param source_url: 当前页面的URL
    :param extract_url: 从当前页面元素中提取的URL
    :return: 补全的URL
    """
    if extract_url.startswith('http'):
        # 包含http开头不需要处理
        return extract_url
    source_url_info = urlparse(source_url)
    if extract_url.startswith('//'):
        # 需要补全http部分
        return source_url_info.scheme + extract_url
    else:
        # 需要补全域名部分
        return source_url_info.scheme + '://' + source_url_info.netloc + extract_url


def crawl_chapter_urls(chapter_index_url: str, crawl_config: CrawlConfig) -> list:
    """
    爬取章节目录
    :param chapter_index_url: 章节目录页面地址
    :param crawl_config: 爬取配置
    :return: 章节列表
    """
    html_content = u_file.get_content_with_cache(chapter_index_url, **REQUESTS_KWARGS)
    soup = BeautifulSoup(html_content, 'lxml')

    chapter_url_nodes = soup.select(crawl_config.chapter_url_selector)
    log.info('crawl chapter html content finish. chapter url sizes: {}'.format(len(chapter_url_nodes)))

    chapter_urls = []
    for chapter_url_node in chapter_url_nodes:
        if not chapter_url_node or '#' == chapter_url_node['href']:
            log.warn('skip empty chapter url: {}'.format(chapter_url_node))
            continue
        chapter_index_url = {
            'title': chapter_url_node['title'],
            'url': patch_url(chapter_index_url, chapter_url_node['href'])
        }
        chapter_urls.append(chapter_index_url)

    log.info('crawl chapter url finish. size: {}'.format(len(chapter_urls)))

    # 处理分页章节爬取
    return chapter_urls


def crawl_chapter_content(chapter_url: str, crawl_config: CrawlConfig) -> str:
    """
    爬取某一章节的内容
    :param chapter_url: 章节内容url
    :param crawl_config: 爬取配置
    :return: 章节内容
    """
    chapter_content = u_file.get_content_with_cache(chapter_url, **REQUESTS_KWARGS)
    chapter_soup = BeautifulSoup(chapter_content, 'lxml')
    chapter_content_p_nodes = chapter_soup.select(crawl_config.chapter_content_selector)
    if not chapter_content_p_nodes:
        log.error('get chapter content empty. chapter_url: {}'.format(chapter_url))
        return ''
    chapter_content = ''
    for chapter_content_p_node in chapter_content_p_nodes:
        chapter_content += chapter_content_p_node.text.strip() + '\n'
    return chapter_content


def crawl_novel_by_menu(chapter_index_url: str, novel_title: str):
    """
    从小说章节目录主页爬取小说，首先获取所有的章节，然后依次爬取每个章节
    :param chapter_index_url:  章节目录页面地址
    :param novel_title: 小说标题
    :return:
    """
    crawl_config = get_crawl_config(chapter_index_url)
    log.info('crawl config')
    chapter_urls = crawl_chapter_urls(chapter_index_url, crawl_config)
    novel_content = ''
    novel_save_path = f'result\\{novel_title}.txt'

    for chapter_url in chapter_urls:
        log.info('----> begin crawl chapter: {}'.format(chapter_url))
        novel_content += '\n\n' + chapter_url['title'] + '\n\n'
        chapter_content = crawl_chapter_content(chapter_url['url'], crawl_config)
        if not chapter_content or len(chapter_content) <= 100:
            log.error('chapter content is less. chapter_url: {}, content: {}'.format(chapter_url, chapter_content))
            continue
        novel_content += chapter_content
        u_file.write_content(novel_save_path, novel_content)


def crawl_novel_by_next(begin_chapter_url: str, novel_title: str):
    """
    通过不断爬取下一章来爬取小说内容，从第一章开始直到最后一章
    :param begin_chapter_url: 小说第一章内容
    :param novel_title: 小说标题
    :return: 小说完整内容
    """
    novel_save_path = f'result\\{novel_title}.txt'

    novel_content = ''
    next_chapter_url = begin_chapter_url
    crawl_config = get_crawl_config(begin_chapter_url)
    while next_chapter_url:
        log.info('begin crawl url: {}'.format(next_chapter_url))
        html_content = u_file.get_content_with_cache(next_chapter_url, **REQUESTS_KWARGS)

        if not html_content:
            log.error('crawl error for url: {}'.format(next_chapter_url))
            continue

        chapter_soup = BeautifulSoup(html_content, 'lxml')

        # 获取下一章的url
        next_chapter_url_node = chapter_soup.select_one(crawl_config.next_chapter_url_selector)
        if next_chapter_url_node:
            next_chapter_url = patch_url(begin_chapter_url, next_chapter_url_node['href'])

        # 章节标题
        chapter_title_node = chapter_soup.select_one(crawl_config.chapter_title_selector)
        novel_content += '\n\n' + chapter_title_node.text + '\n'

        # 章节内容
        chapter_content_node = chapter_soup.select_one(crawl_config.chapter_content_selector)
        chapter_content = chapter_content_node.text
        if len(chapter_content) <= 500:
            log.error('content is less: {}'.format(next_chapter_url))
            continue
        novel_content += chapter_content

        u_file.write_content(novel_save_path, novel_content)
    return novel_content


if __name__ == '__main__':
    crawl_novel_by_next('https://ncode.syosetu.com/n6316bn/1/', '転生したらスライムだった件')
    # crawl_novel_by_next('https://325def1d9a6.12bqg.com/book/152211/1.html', '转生冰山大小姐也不要被她们贴')
