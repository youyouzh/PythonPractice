import os
import json
import time
import requests
import hashlib
import gzip
import zipfile
import base64
import xmltodict
from Crypto.Cipher import AES
from u_base import u_log as log
from u_base import u_file
from u_base.u_file import m_get

HEADERS = {
    'User-Agent': 'HJApp%201.0/android/SM-G9550/4c1639cf6f4b2ecb0068ac4/7.1.2/com.hujiang.dict/3.6.1.279/miui/ '
                  'deviceId/4c1639cf6f4b2ecb0068ac4',
    # 'X-B3-TraceId': '4547fdb6b51fabe4',
    # 'Device-Id': '4c1639cf6f4b2ecb0068ac4',
    # 'X-B3-Sampled': '1',
    # 'X-B3-SpanId': '4547fdb6b51fabe4',
    # 'TracetNo': 'NULuLUGaNcf='
}
AUTH_HEADERS = HEADERS.copy()
AUTH_HEADERS['Access-Token'] = '0009194865.b36c6f34d9d899b424c1516f71d1dc4a'


def get_word_books(category: str = '日语') -> list:
    """
    获取某个分类的单词书列表，大分类有：日语，英语，还可以包含小分类
    :param category: 分类
    :return: 词书列表
    """
    url = 'http://cichang.hjapi.com/v3/book/search_by_tag'
    cache_file = r'result/word-books/{}.json'.format(category)
    u_file.ready_dir(cache_file)
    if os.path.isfile(cache_file):
        return list(u_file.load_json_from_file(cache_file))
    params = {
        'sort': 'Popular',  # 默认排序
        'query': category,
        'start': 0,  # 这个参数其实是页数，pageIndex
        'limit': 200  # 日语词书只有189本
    }
    response = u_file.get_json(url, params, headers=HEADERS)
    word_books = u_file.m_get(response, 'data.items')
    if word_books is None:
        log.error('The response has not data.items field.')
        return []
    log.info('get word books success. size: {}, total: {}'
             .format(len(word_books), u_file.m_get(response, 'data.totalCount')))
    word_books = sorted(word_books, key=lambda x: x['userCount'], reverse=True)  # 按照学习人数倒序排序
    u_file.cache_json(word_books, cache_file)
    return word_books


def get_word_book_resources(word_book_id: int, word_book_name: str) -> dict:
    """
    获取单词书资源信息，词书资源的压缩包下载地址
    :param word_book_id:  词书id
    :param word_book_name:  词书名
    :return: 词书资源列表
    """
    url = 'http://cichang.hjapi.com/v3/user/me/book/{}/resource'.format(word_book_id)
    cache_file = r'result/word-book-resource/{}-{}.json'.format(word_book_name, word_book_id)
    u_file.ready_dir(cache_file)
    if os.path.isfile(cache_file):
        return u_file.load_json_from_file(cache_file)
    response = u_file.get_json(url, headers=AUTH_HEADERS)
    word_book_resources = m_get(response, 'data')

    # 如果提示默认词书不存在，则需要添加默认词书，才可以查询，查询到结果后删除掉词书
    if response.get('message') == '默认词书不存在':
        # 需要添加默认词书才可以查询数据
        log.info('The word book is not default. word_book_id: {}'.format(word_book_id))
        add_default_url = 'https://cichang.hjapi.com/v3/user/me/book/{}/default'.format(word_book_id)
        delete_default_url = 'https://cichang.hjapi.com/v3/user/me/book/{}'.format(word_book_id)
        requests.put(add_default_url, headers=AUTH_HEADERS, verify=False)
        response = u_file.get_json(url, headers=AUTH_HEADERS)
        word_book_resources = m_get(response, 'data')
        requests.delete(delete_default_url, headers=AUTH_HEADERS, verify=False)
        log.info('add word book to default then delete. word_book_id: {}'.format(word_book_id))

    if word_book_resources is None:
        log.error('get word book resources failed. response: {}'.format(response))
        return {}
    u_file.cache_json(word_book_resources, cache_file)
    return word_book_resources


def download_decrypt_word_book_resource(word_book: dict, word_book_resource: dict) -> list:
    """
    下载并解压词书资源，app新版使用的是 textXMLResource，但是是xml格式
    :param word_book: 词书信息
    :param word_book_resource: 词书资源信息，get_word_book_resources的返回值
    :return:
    """
    # 提取压缩包下载地址，以及版本号
    resource = word_book_resource.get('textXMLResource')
    resource_url = resource.get('url')
    resource_version = resource.get('version')
    unzip_password = generate_unzip_password(resource_version)
    resource_save_file = u_file.covert_url_to_filename(resource_url, with_domain=False)

    # 下载压缩包
    log.info('begin download resource file. url: {}, size: {}MB'
             .format(resource_url, round(resource.get('zipSize') / 1024 / 1024, 2)))
    resource_save_file = os.path.join(r'result/zip/', resource_save_file)
    u_file.download_file(resource_url, resource_save_file, verify=False)

    # 解压缩文件
    word_book_tag = '{}-{}-{}'.format(word_book['name'], word_book['id'], resource['version'])
    zip_target_path = r'result/word-book-zip/{}.xml.zip'.format(word_book_tag)
    word_book_item_file = r'result/word-book-zip/{}-xml-word.txt'.format(word_book_tag)
    word_book_item_json_file = r'result/word-book-json/{}.json'.format(word_book_tag)
    u_file.ready_dir(zip_target_path)
    u_file.ready_dir(word_book_item_file)
    u_file.ready_dir(word_book_item_json_file)
    if os.path.isfile(word_book_item_json_file):
        log.info('load word book item json from cache file: {}'.format(word_book_item_json_file))
        return list(u_file.load_json_from_file(word_book_item_json_file))

    if os.path.isfile(word_book_item_file):
        # 如果词书文件已经存在，则已经解压缩过，直接从文件加载
        log.info('The word book item file is exist, load data from file: {}'.format(word_book_item_file))
        with open(word_book_item_file, 'rb') as fin:
            word_book_items_content = fin.read()
    else:
        # 从压缩文件中提取词书文件，并读取内容，总共三个文件，只用到 word.txt
        log.info('begin unzip file: {}'.format(resource_save_file))
        zip_file = zipfile.ZipFile(resource_save_file, 'r')
        u_file.ready_dir(zip_target_path)
        log.info('unzip success. files: {}'.format(zip_file.namelist()))
        sub_files = zip_file.namelist()
        if 'word.txt' not in sub_files:
            log.error('There is not word.txt file in the zip archive.')
            return []
        word_book_items_content = zip_file.read('word.txt', pwd=unzip_password.encode('UTF-8')).decode('UTF-8')
        u_file.write_content(word_book_item_file, word_book_items_content)
        log.info('unzip and extract file word.txt success.')
    log.info('load word book item content. size: {}'.format(len(word_book_items_content)))
    word_book_items = xmltodict.parse(word_book_items_content)
    word_book_items = m_get(word_book_items, 'ArrayOfBookItem.BookItem')
    log.info('convert xml to dict success. word book items size: {}'.format(len(word_book_items)))

    # 提取和解密词书中的单词字段
    word_book_item_infos = []
    for book_item in word_book_items:
        word_book_item_info = {
            'ItemID': m_get(book_item, 'ItemID'),
            'BookID': m_get(book_item, 'BookID'),
            'UnitID': m_get(book_item, 'UnitID'),
            'Word': m_get(book_item, 'Word'),
            'WordID': m_get(book_item, 'WordID'),
            'WordPhonetic': m_get(book_item, 'WordPhonetic'),
            'WordTone': m_get(book_item, 'WordTone'),
            'WordDef': decode_field(m_get(book_item, 'WordDef')),
            'WordRomaji': decode_field(m_get(book_item, 'WordRomaji')),
            'WordAudio': decode_field(m_get(book_item, 'WordAudio')),
            'Langs': m_get(book_item, 'Langs'),
            'SentenceID': m_get(book_item, 'SentenceID'),
            'Sentence': decode_field(m_get(book_item, 'Sentence')),
            'SentenceDef': decode_field(m_get(book_item, 'SentenceDef')),
            'SentenceAudio': decode_field(m_get(book_item, 'SentenceAudio')),
            'YuliaokuWordId': m_get(book_item, 'YuliaokuWordId'),
            'WordExtJson': decode_field(m_get(book_item, 'WordExtJson')),
        }
        word = m_get(book_item, 'Word')

        # 提取单词题目选项列表
        options = m_get(book_item, 'Options.Subject')
        if not isinstance(options, list):
            options = [options]
        log.info('extract options. word: {}, options size: {}'.format(word, len(options)))
        option_infos = []
        for option in options:
            option_info = {
                'Content': decode_field(m_get(option, 'Content')),
                'DefId': m_get(option, 'DefId'),
                'Status': m_get(option, 'Status'),
                'SubType': m_get(option, 'SubType'),
                'Right': decode_field(m_get(option, 'Right')),
                'MixItems': list(map(lambda x: decode_field(x), m_get(option, 'MixItems.Item')))
                if m_get(option, 'MixItems.Item') is not None else [],
                'Phase': decode_field(m_get(option, 'Phase')),
                'QuestionContent': decode_field(m_get(option, 'QuestionDetailType.Content')),
                'QuestionContentDescription': decode_field(m_get(option, 'QuestionDetailType.Description')),
                'QuestionHint': decode_field(m_get(option, 'QuestionDetailType.Hint')),
                'QuestionMixItem': decode_field(m_get(option, 'QuestionDetailType.MixItem')),
                'QuestionType': decode_field(m_get(option, 'QuestionDetailType.Type')),
                'QuestionTypeName': decode_field(m_get(option, 'QuestionDetailType.TypeName')),
            }
            # 混淆项的处理
            mix_items = m_get(option, 'MixItems.Item')
            if mix_items is None:
                mix_items = []
            elif isinstance(mix_items, list):
                mix_items = list(map(lambda x: decode_field(x), mix_items))
            else:
                # 只有一个选项，转成数组
                mix_items = decode_field(mix_items)
            option_info['MixItems'] = mix_items
            option_infos.append(option_info)
        word_book_item_info['Options'] = option_infos

        # 提取单词释义列表
        definition_infos = []
        definitions = m_get(book_item, 'Definitions.Definition', [])
        if not isinstance(definitions, list):
            # 有些情况只有一个释义而不是数组，xml转成json会变成dict，需要包装成list，否则下面的循环为有问题
            definitions = [definitions]
        log.info('extract definitions. word: {}, definitions size: {}'.format(word, len(definitions)))
        for definition in definitions:
            # 释义句子，例句
            sentence_infos = []
            sentences = m_get(definition, 'Sentences.Item', [])
            if not isinstance(sentences, list):
                # 只有一个句子的case需要包装一下
                sentences = [sentences]
            log.info('extract sentences. word: {}, sentences size: {}'.format(word, len(sentences)))
            for sentence in sentences:
                sentence_infos.append({
                    'SentId': m_get(sentence, 'SentId'),
                    'AudioUrl': decode_field(m_get(sentence, 'AudioUrl')),
                    'SentText': decode_field(m_get(sentence, 'SentText')),
                    'Translation': decode_field(m_get(sentence, 'Translation')),
                })
            definition_infos.append({
                'Collocations': '',
                'DefId': m_get(definition, 'SubType'),
                'Pos': decode_field(m_get(definition, 'Pos')),
                'DefValue': decode_field(m_get(definition, 'DefValue')),
                'Sentences': sentence_infos,
            })
        word_book_item_info['Definitions'] = definition_infos

        word_book_item_infos.append(word_book_item_info)
    log.info('decrypt word book items success. item size: {}'.format(len(word_book_items)))
    u_file.cache_json(word_book_item_infos, word_book_item_json_file)
    return word_book_item_infos


def generate_unzip_password(version: int) -> str:
    """
    沪江下载的词书压缩文件是有密码的，密码通过版本号计算得到
    test version: 2110131156  => zc7Oz87Mzs7KyQ==
    :param version: 词书压缩包版本号
    :return: 密码
    """
    version = str(version).encode('UTF-8')
    not_md5 = []
    for byte in version:
        not_md5.append(byte ^ 0xFF)
    not_md5 = bytes(not_md5)
    password = base64.standard_b64encode(not_md5)
    password = password.decode("UTF-8")
    log.info('generate unzip password success: {}'.format(password))
    return password


def decode_field(encode_content: str) -> str:
    """ShoppingDetailsBiz
    沪江词汇解压缩后，其中结构字段内容也是加密的，需要解密
    test str: 'HHxTHHxiHHxDHHx3HH1tGWRHHH5wHH5gHH1+HH5UpBx8eBx8Qxx9QKIcfW0WZHkcfX4cfXQcf30='
    :param encode_content: 加密文本
    :return: 解密后的文本
    """
    if encode_content is None or encode_content == '' or encode_content.strip() == '':
        # log.info('The encode content is blank')
        return ''
    encode_content = encode_content.encode('UTF-8')
    decode_content = base64.standard_b64decode(encode_content)
    decode_bytes = []
    for byte in decode_content:
        decode_bytes.append(byte ^ 0xFF)
    decode_bytes = bytes(decode_bytes)
    decode_str = decode_bytes.decode('UTF-8')
    # log.info('decode success, from {} -> {}'.format(encode_content, decode_str))
    return decode_str


def get_word_detail(word: str, from_lang='jp', to_lang='cn', detail=False, retry_times=5) -> dict:
    api_url = 'http://dict.hjapi.com/v10/{}/{}/{}'.format('dict' if detail else 'quick', from_lang, to_lang)
    word_ext = ''
    cache_file = r'result/word-{}-{}/{}.json'.format(from_lang, to_lang, word)
    u_file.ready_dir(cache_file)
    if os.path.isfile(cache_file):
        log.info('load word detail from cache file: {}'.format(cache_file))
        return u_file.load_json_from_file(cache_file)
    app_secret = '3be65a6f99e98524e21e5dd8f85e2a9b'
    sign_str = 'FromLang={}&ToLang={}&Word={}&Word_Ext={}{}' \
        .format(from_lang, to_lang, word, word_ext, app_secret).encode(encoding='UTF-8')
    headers = AUTH_HEADERS.copy()
    headers['hujiang-appkey'] = 'b458dd683e237054f9a7302235dee675'
    headers['hujiang-appsign'] = hashlib.md5(sign_str).hexdigest().upper()
    response = requests.post(
        api_url,
        data={
            "word": word,
            "word_ext": None
        },
        headers=headers,
        verify=False
    )
    log.info('end get info from web url: ' + api_url)
    if not (400 <= response.status_code < 500):
        response.raise_for_status()
    if response.text is None or response.text == '':
        log.error('The response text is empty.')
    query_result = json.loads(response.text)
    if 'data' not in query_result or query_result.get('status', -1) != 0:
        log.error('The response is not valid: {}'.format(response.text))
        if retry_times >= 0 and 'Abnormal request' == query_result['message']:
            sleep_seconds = 60 * (5 - retry_times)
            log.info('retry query and sleep. times: {}, sleep seconds: {}'.format(retry_times, sleep_seconds))
            time.sleep(sleep_seconds)
            return get_word_detail(word, from_lang, to_lang, detail, retry_times - 1)
        return {}
    time.sleep(0.5)
    word_result = aes_cbc_decrypt_word_data(query_result['data']) if detail else query_result['data']
    u_file.cache_json(word_result, cache_file)
    return word_result


def aes_cbc_decrypt_word_data(encode_data):
    """
    沪江小D单词详情查询接口返回的 data 是加密的，需要解密，AES_CBC解密
    :param encode_data: 加密数据
    :return: 解密后的json数据
    """
    key = 'ceh[Een,3d3o9neg}fH+Jx4XiA0,D1cT'.encode('UTF-8')
    iv = 'K+\\~d4,Ir)b$=paf'.encode('UTF-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # 解密之前还需要 base64解码
    decode_data = base64.decodebytes(encode_data.encode('UTF-8'))
    decode_data = cipher.decrypt(decode_data)

    # 注意需要去掉尾部的填充字符，复杂解压失败
    decode_data = decode_data[:-decode_data[-1]]
    decode_data = gzip.decompress(decode_data)
    decode_data = json.loads(decode_data.decode('UTF-8'))
    log.info('decode word detail data success.')
    return decode_data


def download_word_books(category: str = '日语', size: int = 60, word_book_id=None, query_word=False):
    """
    下载词书数据，包括词书题目等
    :param category: 分类
    :param size: 下载的词书数量，按照添加用户倒序排序
    :param word_book_id: 指定下载单词书id
    :param query_word: 是否查询单词详情
    :return:
    """
    log.info('--->begin download word books. category: {}, size: {}'.format(category, size))
    word_books = get_word_books(category)
    index = 0
    for word_book in word_books:
        if word_book_id is not None and word_book['id'] != word_book_id:
            continue
        if index >= size:
            break
        log.info('--->begin crawl word book id: {}, name: {}'.format(word_book['id'], word_book['name']))
        word_book_resource = get_word_book_resources(word_book['id'], word_book['name'])
        word_book_item_infos = download_decrypt_word_book_resource(word_book, word_book_resource)
        if query_word:
            queried_count = 1
            for word_book_item_info in word_book_item_infos:
                word = word_book_item_info['Word']
                get_word_detail(word, detail=True)
                log.info('get word detail success. word: {}, progress:[{}/{}]'
                         .format(word, queried_count, len(word_book_item_infos)))
                queried_count += 1
        log.info('--->end crawl word book id: {}, name: {}'.format(word_book['id'], word_book['name']))
        index += 1
    log.info('--->end download word books. category: {}, size: {}'.format(category, size))


if __name__ == '__main__':
    log.info('begin process')
    download_word_books('日语', query_word=True, word_book_id=13216)
    # get_word_detail('詰め', detail=True)
    # grammar_json_file_path = r'./result/grammar-n5.json'
