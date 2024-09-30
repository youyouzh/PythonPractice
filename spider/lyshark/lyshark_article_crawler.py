"""
爬取LyShark的文章列表，并按照文章结构进行拼接处理方便阅读
"""
import json
import os.path
import re
import time
from typing import List

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from u_base import u_file
from u_base.u_log import logger


def crawl_article_archives(index_url: str, max_page_count: int = 50, use_cache: bool = True) -> List[dict]:
    """
    爬取当前页归档的文章列表
    :param use_cache: 是否使用缓存
    :param index_url: 归档首页页地址
    :param max_page_count: 爬取最大页数
    :return: 所有归档的文章列表
    """
    cache_filepath = os.path.join(r'cache', 'article_archives.json')
    # check the cache is exist or not
    if use_cache and os.path.isfile(cache_filepath):
        logger.info('load article archives from cache: {}'.format(cache_filepath))
        return u_file.load_json_from_file(cache_filepath)

    # 从index_url中获取http链接前缀
    parsed_url = urlparse(index_url)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc

    page_index = 1
    all_articles = []
    next_page_url = index_url
    while page_index <= max_page_count:
        # request html content and parse
        logger.info('begin request {} page_url: {}'.format(page_index, next_page_url))
        html_cache_filepath = os.path.join('cache', 'article_archives_page_{}.html'.format(page_index))
        html_content = u_file.get_content_with_cache(next_page_url, encoding='utf-8', cache_file=html_cache_filepath)
        soup = BeautifulSoup(html_content, 'lxml')

        # parse article nodes, generally 10 articles per page
        article_nodes = soup.select('a.post-title-link')
        logger.info('query article nodes size: {}'.format(len(article_nodes)))
        if not article_nodes:
            logger.info('current page has no article, crawl end. page_index: {}'.format(page_index))
            break

        # parse article info, contains title and url
        all_articles.extend([{'title': node.select_one('span').text, 'url': base_url + node['href']}
                             for node in article_nodes])

        # continue next page crawl
        page_index += 1
        next_page_url = base_url + f'/archives/page/{page_index}/'
        time.sleep(2)

    # save to cache
    u_file.dump_json_to_file(cache_filepath, all_articles)
    return all_articles


def extract_article_content(article_url: str) -> str:
    logger.info('begin request article url: {}'.format(article_url))
    html_content = u_file.get_content_with_cache(article_url, encoding='utf-8')
    soup = BeautifulSoup(html_content, 'lxml')

    article_content_node = soup.select_one('div.post-body')
    if not article_content_node:
        logger.error('The article content node is empty.')
        return ''
    # 返回文章的html文本
    return article_content_node.decode_contents()


def patch_all_article_content(articles: List[dict]) -> List[dict]:
    """
    补充爬取所有文章内容
    :param articles: 文章信息
    :return: 补全后的文章信息
    """
    for article in articles:
        article['content'] = extract_article_content(article['url'])
    return articles


def merge_article_by_menu(menu_titles: List[str], articles: List[dict]):
    """
    按照菜单进行排序
    :param menu_titles: 菜单列表
    :param articles: 文章列表
    :return: 排序后的文章列表
    """
    html_content = ''
    for menu_title in menu_titles:
        # 找到匹配的文章内容
        menu_articles = [article for article in articles if menu_title in article['title']]
        if not menu_articles:
            logger.warning('No article found for menu: {}'.format(menu_title))
            continue
        html_content += '<h2>{}</h2><p></p>'.format(menu_title)
    merge_html_template = u_file.get_content('merge_html_template.html')
    merge_html_template.replace('{{article_content}}', html_content)
    u_file.write_content('merged_content.html', merge_html_template)


def parse_toc_titles(toc_filepath: str) -> List[str]:
    lines = u_file.read_file_as_list(toc_filepath)
    format_titles = []
    for line in lines:
        format_titles.append(re.sub(r'第\S章|篇：(\S+) [\d\.]+', '\1', line))
        format_titles.append(re.sub(r'[\d\.] (\s+) [\d\.]+', '\1', line))
    return format_titles


if __name__ == '__main__':
    # articles = crawl_article_archives('https://www.lyshark.com/archives/', max_page_count=44, use_cache=False)
    print(extract_article_content('https://www.lyshark.com/post/7524b3ac.html'))
