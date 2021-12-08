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
    sign_str = 'FromLang={}&ToLang={}&Word={}&Word_Ext=3be65a6f99e98524e21e5dd8f85e2a9b'\
        .format(from_lang, to_lang, word).encode(encoding='UTF-8')
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
    key = 'ceh[Een,3d3o9neg}fH+Jx4XiA0,D1cT'.encode('UTF-8')
    iv = 'K+\\~d4,Ir)b$=paf'.encode('UTF-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decode_data = base64.decodebytes(encode_data.encode('UTF-8'))

    decode_data = cipher.decrypt(decode_data)
    decode_data = decode_data[:-decode_data[-1]]
    decode_data = gzip.decompress(decode_data)
    decode_data = json.loads(decode_data.decode('UTF-8'))
    return decode_data


if __name__ == '__main__':
    # grammar_json_file_path = r'./result/grammar-n5.json'
    # parse_and_save_jiemo_grammar_json(grammar_json_file_path)
    # query_hujiang_word("上")
    word = '外す'
    result = query_hujiang_word(word, 'jp', 'cn', True)
    u_file.cache_json(result, r'result/{}.json'.format(word))
    print(result)
