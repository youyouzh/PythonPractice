#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests, re, json
from bs4 import BeautifulSoup

# global config
config = {
    'begin_article': 0, # 开始扫描的文章数，便于继续扫描
    'max_article': 10,   # 扫描的最大文章数
    'console_output': True, # 是否控制台输出
    'template_input_html' : 'page/input.html', # 输入HTML路径，控制显示样式
    'output_html_path' : 'page/output.html', # 输出HTML路径，空则不输出
    'output_json_path' : 'page/result.json', # 输出json路径，空则不输出
}

# 控制台统一输出
def console_print(message):
    if config['console_output']:
        print(message)

# get the content from the http url or local path
def get_content(url = ''):
    if not url:
        return False
    # if url is not http url try use local path, read from local page
    if url.find('http') < 0:
        fin = open(url, 'r', encoding='UTF-8')
        html_content = fin.read()
        return html_content
    try:
        #herders = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}
        console_print('begin get info from web url: ' + url)
        # time.sleep(0.5)
        response = requests.get(url, timeout=60)
        console_print('end get info from web url: ' + url)
        if not (400 <= response.status_code < 500):
            response.raise_for_status()
        return response.text
    except Exception:
        return False

# scan the main page, get all article urls and the next page url
def scan_main_page(url):
    html_content = get_content(url)
    if not html_content:
        return False
    console_print('begin analysis url: ' + url)
    soup = BeautifulSoup(html_content, 'lxml')
    # find the article nodes
    article_nodes = soup.find_all('article')
    if not article_nodes:
        return False
    articles = []
    # find all article url
    for node in article_nodes:
        # article contain header,div,footer
        article_id = int(node['id'].split('-')[1]) # node['id']:post-6355
        if 2958 == article_id:    # skip the first advertised
            continue

        header_node = node.header  # the header node
        a_node = header_node.h1.a  # the title a element

        # get the author and time
        meta_node = header_node.find('div', {'class': 'entry-meta'})
        time_node = meta_node.find('a')
        data_node = meta_node.find('time')
        author_node = meta_node.find('span', {'class': 'author'})
        articles.append({
            'id': article_id,
            'title' : a_node.string,
            'url': a_node['href'],
            'author': author_node.a.string,
            'date': data_node.string,
            'time': time_node['title']
        })
        console_print('get the page id:' + str(article_id) + ' title is:'+ str(a_node.string))

    # find the next page url
    page_nav = soup.find('div', {'class': 'wp-pagenavi'})
    next_url = page_nav.find('a', {'class': 'larger'})['href']
    page_info = {
        'articles' : articles,
        'next' : next_url
    }
    return page_info

# scan article page,get the article info
def scan_article_page(url):
    html_content = get_content(url)
    if not html_content:
        return False
    console_print('begin analysis the page: ' + url)
    soup = BeautifulSoup(html_content, 'lxml')
    header_node = soup.find('header', {'class': 'entry-header'})
    if not header_node:   # unexpected page content
        console_print('unexpected page')
        return False
    header_a_nodes = header_node.find_all('a')
    article = {
        'date': header_a_nodes[0].string,
        'author': header_a_nodes[1].string,
        'title': header_node.h1.string
    }

    article_content_node = soup.find('div', {'class': 'entry-content'})  # find the content node
    # delete the non-content node
    nav_nodes = article_content_node.find_all('div', {'class': 'nav-hidden'})
    recommend_node = article_content_node.find('div', {'class': 'yarpp-related'})
    for div_node in nav_nodes:
        div_node.extract()
    recommend_node.extract()

    # get all article image
    image_urls = []
    image_nodes = article_content_node.find_all('img')    # find all image tag
    for node in image_nodes:
        image_urls.append(node['src'])  # get all image url
    article['images'] = image_urls

    # get all article magnet
    magnet_urls = []
    magnet_nodes = article_content_node.find_all('p', text=re.compile('[0-9a-zA-Z]{10}[0-9a-zA-Z]+'))
    for node in magnet_nodes:
        magnet_urls.append(node.string)
    #if not find any magnet code, try find baidupan code or other mystical code
    if not magnet_urls:
        mystical_code_nodes = article_content_node.find_all(text=re.compile('[0-9a-zA-Z]{6}'))
        for node in mystical_code_nodes:
            magnet_urls.append(node.string)
    article['magnet'] = magnet_urls
    console_print('end analysis, get images: ' + str(len(image_urls)) + ' magnet: ' + str(len(magnet_urls)))
    return article

# begin driver
def driver(url):
    if not url:
        return False
    next_url = url
    # limit the scan page counts
    article_count = 0
    articles = []
    while next_url and article_count < config['max_article']:
        article_info = scan_main_page(next_url)
        if not article_info:
            return False
        for article in article_info['articles']:
            article_count += 1
            # 略过开始扫描配置，便于继续扫描
            if not article or article_count <= config['begin_article']:
                continue
            page_info = scan_article_page(article['url'])
            if not page_info:
                continue
            articles.append({
                'id' : article['id'],
                'title' :article['title'],
                'url' : article['url'],
                'author' : article['author'],
                'date' : article['date'],
                'time' : article['time'],
                'images' : page_info['images'],
                'magnet' : page_info['magnet']
            })
            # limit the web page

        # read the next page
        next_url = article_info['next']
        console_print('begin scan the next page:' + next_url)
    console_print('begin write to html file')
    # 将结果保存到HTML
    put_to_html(articles)
    console_print('end write')
    console_print('begin write to json file')
    # 将结果保存到json
    put_to_json(articles)
    console_print('end write')
    return articles

# put the result to html
def put_to_html(articles):
    if not config['template_input_html'] or not config['output_html_path']:
        return False
    path_input = config['template_input_html']
    path_output = config['output_html_path']
    # 加载输入HTML模板
    fin = open(path_input, 'r', encoding='UTF-8')
    # 加载输出模板
    fout = open(path_output, 'w+', encoding='UTF-8')
    soup = BeautifulSoup(fin.read(), 'lxml')
    body = soup.find('body')
    # 构造文章 div 节点
    for article in articles:
        # 文章标题节点
        title_node = soup.new_tag('h2')
        title = soup.new_string(article['title'])
        title_node.append(title)

        # 图片节点
        div_image_node = soup.new_tag('div', {'class': 'image'})
        # 神秘代码节点
        div_magnet_node = soup.new_tag('div', {'class': 'magnet'})
        div_node = soup.new_tag('div', {'class': 'article'})
        for image in article['images']:
            image_node = soup.new_tag('img', src=image)
            div_image_node.append(image_node)
        for magnet in article['magnet']:
            magnet_string = soup.new_string(magnet)
            magnet_node = soup.new_tag('p')
            magnet_node.append(magnet_string)
            div_magnet_node.append(magnet_node)
        # 依次将文章节点添加到模板页面的 body 中
        div_node.append(title_node)
        div_node.append(div_magnet_node)
        div_node.append(div_image_node)
        body.append(div_node)
    # 将HTML页面格式化输出到本地
    fout.write(soup.prettify())

# put the result to json
def put_to_json(articles):
    if not config['output_json_path']:
        return False
    fout = open(config['output_json_path'], 'w', encoding='UTF-8')
    json.dump(articles, fout, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    home_url = 'http://www.hacg.dog/wp/category/all/game/'
    home_path = 'page/main.html'
    article_url = 'http://www.hacg.dog/wp/all/game/%E5%AE%98%E6%96%B9%E7%B9%81%E4%B8%ADadult-versionkarakara2/'
    # scan_page(home_url, 0)
    # console_print(scan_main_page(home_url))
    # console_print(scan_article_page(article_url))
    driver(home_url)