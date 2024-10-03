"""
爬取LyShark的文章列表，并按照文章结构进行拼接处理方便阅读
"""
import os.path
import time
from typing import List
from urllib.parse import urlparse

from bs4 import BeautifulSoup

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
    cache_filepath = os.path.join(r'result', 'article_archives.json')
    # check the cache is exist or not
    u_file.ready_dir(cache_filepath)
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
        time.sleep(1)

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
    lines = u_file.read_file_as_list(toc_filepath, remove_repeat=False)
    format_titles = []
    for line in lines:
        format_title = line
        # format_title = re.sub(r'第\S章|篇：(\S+) [\d\.]+', '\1', line)
        # format_title = re.sub(r'[\d\. ]+(\S+)[ \d\.]+', '\1', format_title)
        format_titles.append(format_title)
    return format_titles


def calculate_longest_common_substr_ratio(str1: str, str2: str) -> int:
    """
    计算两个字符串的相似度，忽略空格
    把两个字符串分别以行和列组成一个二维矩阵；比较二维矩阵中每个点对应行列字符中否相等，相等的话值设置为1，否则设置为0
    计算某个二维矩阵的值的时候顺便计算出来当前最长的公共子串的长度
    :param str1: 原字符串
    :param str2: 目标字符串
    :return: 相识度，0-100，数字越大越相似
    """
    str1 = str1.replace(' ', '')
    str2 = str2.replace(' ', '')

    if len(str1) >= len(str2):
        str1, str2 = str2, str1

    max_match_count = 0
    for i in range(len(str1)):
        current_match_count = 0
        for j in range(len(str2)):
            if i + current_match_count >= len(str1):
                break
            if str1[i + current_match_count] == str2[j]:
                current_match_count += 1
                max_match_count = max(max_match_count, current_match_count)
            j += 1
        i += 1
    return int(max_match_count / len(str1) * 100)


def extract_best_match_title(toc_title: str, article_titles: List[str]) -> str | None:
    """
    查找最匹配的标题
    :param toc_title: 目录中的标题
    :param article_titles: 文章中的标题
    :return:
    """
    # 遍历查找相同字符最多的标题为匹配标题
    max_same_ratio = 0
    best_match_title = None
    for article_title in article_titles:
        ratio = calculate_longest_common_substr_ratio(toc_title, article_title)
        if ratio > max_same_ratio:
            max_same_ratio = ratio
            best_match_title = article_title
    return best_match_title if max_same_ratio >= 40 else None
    # return process.extractOne(toc_title, article_titles, scorer=fuzzywuzzy.fuzz.token_sort_ratio)[0]


def match_toc_title(toc_titles: List[str], article_archives: List[dict]) -> List[dict]:
    match_articles = []
    article_titles = [article['title'] for article in article_archives]
    article_archive_map = {article['title']: article for article in article_archives}
    for toc_title in toc_titles:
        match_article = {'toc_title': toc_title}
        match_title = extract_best_match_title(toc_title, article_titles)
        if match_title:
            article_archive = article_archive_map[match_title]
            match_article['article_title'] = article_archive['title']
            match_article['article_url'] =article_archive['url']
            logger.info('match toc title: {} for article: {}'.format(toc_title, article_archive['title']))
        else:
            logger.warning('match toc title failed for toc title: {}'.format(toc_title))
        match_articles.append(match_article)
    # save data to file
    u_file.dump_json_to_file(r'result\article_archives_match_toc_title.json', match_articles)
    return match_articles


def crawl_main():
    article_archives = crawl_article_archives('https://www.lyshark.com/archives/', max_page_count=44, use_cache=True)
    match_toc_title(parse_toc_titles('灰帽黑客：攻守道.toc.txt'), article_archives)


if __name__ == '__main__':
    crawl_main()
