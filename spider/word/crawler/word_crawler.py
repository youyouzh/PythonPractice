import json
import re
import requests
import hashlib
import gzip
import base64
from Crypto.Cipher import AES
from u_base import u_log as log
from u_base import u_file
from spider.word.database.db import Grammar, save_grammar


def parse_and_save_jiemo_grammar_json(file_path: str):
    grammar_categories = u_file.load_json_from_file(file_path)
    if not grammar_categories or not 'data' in grammar_categories:
        log.warn('The grammar json is invalid: {}'.format(str))
        return

    log.info('load grammar json success. category size: {}'.format(len(grammar_categories)))
    grammar_categories = grammar_categories.get('data')
    for grammar_category in grammar_categories:
        log.info('parse grammar category: {}'.format(grammar_category.get('title')))
        if grammar_category.get('title') != grammar_category.get('label'):
            log.warn('The grammar title and label is not same.')
        grammars = grammar_category.get('grammerList')
        log.info('parse grammar category sub grammar. category: {}, grammar size: {}'
                   .format(grammar_category.get('title'), len(grammars)))
        for grammar in grammars:
            if grammar.get('explain') != grammar.get('comment') or grammar.get('type') != grammar.get('category') \
                    or grammar.get('category') != grammar_category.get('title'):
                log.warn('The grammar category is special. grammar: {}'.format(grammar.get('grammar')))
            log.info('get grammar: {}'.format(grammar.get('grammar')))
            db_grammar = Grammar(id=grammar.get('id'), content=grammar.get('content'))
            db_grammar.level = grammar.get('level')
            db_grammar.category = grammar.get('category')
            db_grammar.type = grammar.get('category')
            db_grammar.link = grammar.get('link')
            db_grammar.explain = grammar.get('explain')
            db_grammar.example = re.sub('[#@][0-9]*', '', grammar.get('exmple'))
            db_grammar.postscript = grammar.get('ps')
            save_grammar(db_grammar)


def query_hujiang_word(word: str, from_lang='cn', to_lang='jp', detail=False) -> dict:
    api_url = 'http://dict.hjapi.com/v10/{}/{}/{}'.format('dict' if detail else 'quick', from_lang, to_lang)
    word_ext = ''
    app_secret = '3be65a6f99e98524e21e5dd8f85e2a9b'
    sign_str = 'FromLang={}&ToLang={}&Word={}&Word_Ext={}{}'\
        .format(from_lang, to_lang, word, word_ext, app_secret).encode(encoding='UTF-8')
    response = requests.post(
        api_url,
        data={
            "word": word,
            "word_ext": None
        },
        headers={
            "User-Agent": u_file.COMMON_USER_AGENT,
            "hujiang-appkey": "b458dd683e237054f9a7302235dee675",
            "hujiang-appsign": hashlib.md5(sign_str).hexdigest()
        },
    )
    log.info('end get info from web url: ' + api_url)
    if not (400 <= response.status_code < 500):
        response.raise_for_status()
    if response.text is None or response.text == '':
        log.error('The response text is empty.')
    query_result = json.loads(response.text)
    if 'data' not in query_result or query_result.get('status', -1) != 0:
        log.error('The response is not valid: {}'.format(response.text))
        return {}
    return hujiang_des_cbc_decrypt(query_result['data']) if detail else query_result['data']


def hujiang_des_cbc_decrypt(encode_data):
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
    return decode_data


def generate_zip_file_password(version: int) -> str:
    """
    沪江下载的词书压缩文件是有密码的，密码通过版本号计算得到
    :param version: 词书压缩包版本号
    :return: 密码
    """
    version = 2110131156
    version = str(version).encode('UTF-8')
    not_md5 = []
    for byte in version:
        not_md5.append(byte ^ 0xFF)
    not_md5 = bytes(not_md5)
    password = base64.standard_b64encode(not_md5)
    print(password)
    return password.decode("UTF-8")


def decode_book_field(encode_content: str) -> str:
    """ShoppingDetailsBiz
    沪江词汇解压缩后，其中的内容也是加密的，需要解密
    :param encode_content: 加密文本
    :return: 解密后的文本
    """
    encode_content = 'HHxTHHxiHHxDHHx3HH1tGWRHHH5wHH5gHH1+HH5UpBx8eBx8Qxx9QKIcfW0WZHkcfX4cfXQcf30='
    encode_content = encode_content.encode('UTF-8')
    decode_content = base64.standard_b64decode(encode_content)
    result = []
    for byte in decode_content:
        result.append(byte ^ 0xFF)
    result = bytes(result)
    print(result.decode('UTF-8'))
    return result.decode('UTF-8')


if __name__ == '__main__':
    # grammar_json_file_path = r'./result/grammar-n5.json'
    # parse_and_save_jiemo_grammar_json(grammar_json_file_path)
    # query_hujiang_word("上")
    # generate_zip_file_password('')
    # decode_book_field('HHxTHHxiHHxDHHx3HH1tGWRHHH5wHH5gHH1+HH5UpBx8eBx8Qxx9QKIcfW0WZHkcfX4cfXQcf30=')
    hujiang_des_cbc_decrypt('')
    # word = '外す'
    # result = query_hujiang_word(word, 'jp', 'cn', True)
    # u_file.cache_json(result, r'result/{}.json'.format(word))
    # print(result)
