"""
百合小说相关下载和处理
主要通过 https://index.tsyuri.com/ 爬取百合小说列表
然后通过 刺猬猫 和 SF轻小说 两个平台爬取小说相关数据，然后对小说进行排序，爬取收藏最多的小说
"""
import json
import os.path
import re

import requests
from urllib.parse import quote
from bs4 import BeautifulSoup

import u_base.u_file as u_file
import u_base.u_log as log
from spider.novel.web_novel_crawler import REQUESTS_KWARGS


def patch_novel_info(novel_info: dict) -> dict:
    """
    爬取小说主页的收藏等数据，以便进行排序筛选
    :param novel_info: 小说信息
    :return: 小说信息
    """
    book_name = novel_info['bookName']
    if novel_info['collectCount']:
        log.info('this book collect info is not need to patch: {}'.format(book_name))
        # return novel_info
    if novel_info['crawlSourceName'] == 'SF轻小说':
        # 首先爬取小说url
        novel_info_index_url = 'https://index.tsyuri.com/book/{}.html'.format(novel_info['id'])
        html_content = u_file.get_content_with_cache(novel_info_index_url, **REQUESTS_KWARGS)
        soup = BeautifulSoup(html_content, 'lxml')

        novel_index_node = soup.select_one('div.layui-col-xs8 > div > a')
        if not novel_index_node:
            log.error('can not extract novel index url: {}'.format(book_name))
            return novel_info
        novel_index_url = novel_index_node['href']
        novel_info['novel_index_url'] = novel_index_url
        log.info('extract novel index url success. book: {}, url: {}'.format(book_name, novel_index_url))

        html_content = u_file.get_content_with_cache(novel_index_url, **REQUESTS_KWARGS)
        soup = BeautifulSoup(html_content, 'lxml')

        book_grade_node = soup.select_one('div#BasicOperation')
        if not book_grade_node:
            log.error('basic grade node is empty. book: {}, url: {}'.format(book_name, novel_index_url))
            return novel_info
        basic_grade_text = book_grade_node.text.replace('\n', '')
        log.info('extract book grade info success. book: {}, text: {}'.format(book_name, basic_grade_text))
        novel_info['likeCount'] = re.compile(r'赞 (\d+)').search(basic_grade_text).groups()[0]
        novel_info['collectCount'] = re.compile(r'收藏 (\d+)').search(basic_grade_text).groups()[0]
        return novel_info
    if novel_info['crawlSourceName'] == '刺猬猫':
        # 搜索小说，然后匹配获取小说页
        search_url = 'https://www.ciweimao.com/get-search-book-list/0-0-0-0-0-0/{}/{}/1'\
            .format(quote('全部'), quote(book_name))
        html_content = u_file.get_content_with_cache(search_url, **REQUESTS_KWARGS)
        soup = BeautifulSoup(html_content, 'lxml')

        search_book_nodes = soup.select('div.cnt > p.tit > a')
        if not search_book_nodes:
            log.error('search book result is empty: {}'.format(book_name))
            return novel_info
        for search_book_node in search_book_nodes:
            if search_book_node['title'] == book_name:
                novel_info['novel_index_url'] = search_book_node['href']
                break
        if 'novel_index_url' not in novel_info or not novel_info['novel_index_url']:
            log.error('search book index url is empty: {}'.format(book_name))
            return novel_info

        html_content = u_file.get_content_with_cache(novel_info['novel_index_url'], **REQUESTS_KWARGS)
        soup = BeautifulSoup(html_content, 'lxml')

        book_grade_node = soup.select_one('p.book-grade')
        if not book_grade_node:
            log.error('basic grade node is empty. book: {}, url: {}'
                      .format(book_name, novel_info['novel_index_url']))
            return novel_info
        basic_grade_text = book_grade_node.text.replace('\n', '')
        log.info('extract book grade info success. book: {}, text: {}'.format(book_name, basic_grade_text))
        novel_info['likeCount'] = re.compile(r'总点击：([,\d.万]+)').search(basic_grade_text).groups()[0]
        novel_info['collectCount'] = re.compile(r'总收藏：(\d+)').search(basic_grade_text).groups()[0]
        return novel_info


def get_novel_list_from_bb(cache_file=''):
    """
    通过请求接口获取百合小说列表，这个接口是一个json请求，可以直接拿到小说的很多数据，获取数据后存入到缓存中
    :param cache_file: 缓存文件路径，如果不为空，则直接从缓存文件中加载
    :return: 小说信息列表
    """
    if cache_file and os.path.isfile(cache_file):
        return u_file.load_json_from_file(cache_file)
    query_api = 'https://index.tsyuri.com/book/searchByPage'
    params = {
        'curr': 1,
        'limit': 100,
        'bookStatus': '1',
        'wordCountMin': 150000,
        'wordCountMax': '',
        'sort': 'click_purity_score',
        'updatePeriod': '',
        'purity': '1',
        'keyword': '',
        # 'tag': '%2C百合',
        'tag': '%2C变百%2C百合',
        'source': '%2CSF轻小说%2C次元姬%2C刺猬猫%2C起点'
    }
    response = requests.get(query_api, params=params)
    if response.status_code != 200:
        log.error('request query api status code not 200.')
        return []
    data = json.loads(response.text)
    if 'code' not in data or data['code'] != '200' or 'data' not in data:
        log.error('response data.code is not 200')
        return []
    data = data['data']
    log.info('page_number: {}, size: {}, total: {}'.format(data['pageNum'], data['pageSize'], data['total']))
    return list(map(lambda x: {
        'id': x['id'],
        'catName': x['catName'],
        'picUrl': x['picUrl'],
        'bookName': x['bookName'],
        'newTag': x['newTag'],
        'authorName': x['authorName'],
        'bookDesc': x['bookDesc'],
        'purity': x['purity'],
        'visitCount': x['visitCount'],
        'likeCount': 0,
        'collectCount': 0,
        'crawlSourceName': x['crawlSourceName'],
        'tag': x['tag'],
    }, data['list']))


def crawl_novel_list():
    book_info_cache_file = r'result\yuri_book_infos.json'
    book_infos = get_novel_list_from_bb(book_info_cache_file)
    for book_info in book_infos:
        log.info('patch book info: {}'.format(book_info['bookName']))
        patch_novel_info(book_info)
        u_file.dump_json_to_file(book_info_cache_file, book_infos)
    book_infos = sorted(book_infos, key=lambda x: int(x['collectCount']), reverse=True)
    u_file.dump_json_to_file(book_info_cache_file, book_infos)


def process_sf():
    """
    处理sf抓包导出的小说内容转存，fiddler导出脚本如上
    // Fiddler自定义抓包导出脚本，使用 boluobao-4.8.22.apk，逍遥模拟器，postern
    // 自动保存session到本地，需将该部分内容加到 OnBeforeResponse 中
    if (oSession.fullUrl.Contains("api.sfacg.com"))
    {
      var mathRegexes = {
        'novel': /\/novels\/(\d+)\?/,
        'chap': /\/Chaps\/(\d+)\?/,
        'dir': /\/novels\/(\d+)\/dirs\?/
      };

      var savePath = "D:/work/crack/nn";
      for (var key in mathRegexes) {
        // 匹配并保存请求
        var matchResult = mathRegexes[key].exec(oSession.fullUrl);
          if (matchResult && matchResult.length >= 2) {
            oSession.SaveSession(savePath + key + '-' + matchResult[1] + '.txt', false);
          }
      }
    }
    """
    save_path = r'D:\work\crack\nn'
    request_files = u_file.get_all_sub_files(save_path, contain_dir=False)

    def read_response_json(file_path: str) -> dict:
        file_content = u_file.read_content(file_path)
        split_token = 'X-Powered-By: ASP.NET'
        split_index = file_content.find(split_token)
        if split_index == -1:
            log.error('The file response is not format.')
            return {}
        return json.loads(file_content[split_index + len(split_token):].strip())

    novel_info_map = {}
    dir_info_map = {}
    chap_content_map = {}

    for request_file in request_files:
        if 'novel' in request_file:
            novel_info = read_response_json(request_file)
            novel_info = novel_info['data']
            novel_info_map[novel_info['novelId']] = novel_info
        if 'dir' in request_file:
            dir_info = read_response_json(request_file)
            dir_info = dir_info['data']
            dir_info_map[dir_info['novelId']] = dir_info
        if 'chap' in request_file:
            chap_content = read_response_json(request_file)
            chap_content = chap_content['data']
            chap_content_map[chap_content['chapId']] = chap_content

    for novel_info in novel_info_map.values():
        novel_id = novel_info['novelId']
        dir_info = dir_info_map[novel_id]
        novel_content = ''
        log.info('begin process novel. id: {}, name: {}'.format(novel_id, novel_info['novelName']))
        for volume in dir_info['volumeList']:
            novel_content += '\n\n{}\n\n'.format(volume['title'])
            for chapter in volume['chapterList']:
                log.info('process novel chapter, novel_id: {}, chapter_id: {}'.format(novel_id, chapter['chapId']))
                novel_content += '\n\n{}\n'.format(chapter['title'])
                chapter_id = chapter['chapId']
                if chapter_id not in chap_content_map:
                    log.warn('The chapter is not download: {}'.format(chapter_id))
                    continue
                novel_content += chap_content_map[chapter_id]['expand']['content']

            u_file.write_content(r'result/r-{}.txt'.format(novel_info['novelName']), novel_content)


if __name__ == '__main__':
    crawl_novel_list()
    # process_sf()
