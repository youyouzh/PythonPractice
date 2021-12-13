import os
import re
import json
import requests
from u_base import u_log as log
from u_base import u_file
from u_base.u_file import m_get
from spider.word.database.db import Grammar, save_grammar

COMMON_PARAMS = {
    "userId": "2669799",
    "timeStamp": "0",
    "G": {
        "at": 12,
        "av": 1900,
        "dt": 1,
        "deviceInfo": {
            "appVersion": "1.9.0",
            "deviceType": "Android",
            "deviceVersion": "5.1.1",
            "mobileBrand": "HUAWEI",
            "mobileModel": "VOG-AL00",
            "screenHeight": 1280,
            "screenWidth": 720,
            "umengChannel": "",
            "versonCode": "1900"
        },
        "deviceId": "47961223-e23c-49d3-98af-3b475c931a62",
        "deviceToken": "AgMZyfgg7LKerXMC5ygeKkKCieYrMLBQiOwLoR2K15G-",
        "umengChannel": "store_qqsj",
        "ddjm": "WdK3VCt58n40oCjIfm8u0kaMcnbTcHfYDoIv3gZiFiDAaMdgJdw2WondIPg3tTKWGyXOFKfRkA-r8Uc9dmtSOZavNix"
                "2swkorhapdD__yUEpH_wCAMqpoCEnjgRdER6badYzEamKn__kpywOpQnYD_sauBfsdYTdHu4ulQSUUC4\u003d"
    }
}


def post_special(url, param: dict = None):
    """
    发送 post 请求，主要是参数中的ddjm等参数，可能用于防火墙拦截
    :param url: url
    :param param: param dict
    :return: 返回json中的data域
    """
    param_json = COMMON_PARAMS.copy()
    param_json.update(param if param is not None else {})
    response = requests.post(url, json=param_json, verify=False)
    log.info('request success. url: {}'.format(url))
    if response.status_code != 200:
        log.info('request failed, status code is not 200. url: {}, code: {}'.format(url, response.status_code))
        return None
    result = json.loads(response.text)
    if m_get(result, 'result') != 0 or m_get(result, 'data') is None:
        log.error('request data is not valid. response: {}'.format(response.text))
        return None
    return m_get(result, 'data')


def crawler_grammar():
    """
    芥末日语考级app，下载所有等级语法讲解json
    :return:
    """
    grammar_url = 'https://ns-api.jiemo.net/v2/NSeries/getGrammarCategroy'
    levels = ['N1', 'N2', 'N3', 'N4', 'N5']
    for level in levels:
        log.info('--->begin download grammar: {}'.format(level))
        grammar_cache_file = r'result\jiemo-grammar\grammar-{}.json'.format(level)
        u_file.ready_dir(grammar_cache_file)
        if os.path.isfile(grammar_cache_file):
            log.info('The grammar is exist. file: {}'.format(grammar_cache_file))
            continue
        param_json = COMMON_PARAMS.copy()
        param_json['level'] = level
        data = post_special(grammar_url, {'level': level})
        if data is None:
            log.info('request grammar failed. level: {}'.format(level))
            continue
        u_file.cache_json(data, grammar_cache_file)
        log.info('--->end download grammar: {}'.format(level))


def crawler_special_knowledge():
    # 词汇变形公式
    formula_url = 'https://ns-api.jiemo.net/v2/book/formulaDetail'
    cache_file = r'result\jiemo-grammar\formula.json'
    if os.path.isfile(cache_file):
        log.info('The formula json is exist: {}'.format(cache_file))
    else:
        data = post_special(formula_url)
        if data is None:
            log.info('request formula failed')
        else:
            log.info('request formula data success')
            u_file.cache_json(data, cache_file)

    # N1考试宝典获取
    exam_book_url = 'https://ns-api.jiemo.net/v2/book/valuableBookDetail'
    cache_file = r'result\jiemo-grammar\exam-book-N1.json'
    if not os.path.isfile(cache_file):
        data = post_special(exam_book_url, {'level': 'N1'})
        if data is None:
            log.info('request exam book N1 failed.')
        else:
            log.info('request exam book N1 success.')
            u_file.cache_json(data, cache_file)

    # N2考试宝典获取
    exam_book_url = 'https://ns-api.jiemo.net/v2/book/valuableBookDetail'
    cache_file = r'result\jiemo-grammar\exam-book-N2.json'
    if not os.path.isfile(cache_file):
        data = post_special(exam_book_url, {'level': 'N2'})
        if data is None:
            log.info('request exam book N2 failed.')
        else:
            log.info('request exam book N2 success.')
            u_file.cache_json(data, cache_file)


def parse_and_save_grammar_json(file_path: str):
    """
    讲语法讲解存入数据库中
    :param file_path:
    :return:
    """
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


def crawler_exam_questions():
    """
    下载所有试卷题目列表
    :return:
    """
    log.info('--->begin crawler exam questions.')
    exam_list_url = 'https://share.jiemo.net/NSeries/getrealQuestionList'
    exam_question_url = 'https://share.jiemo.net/NSeries/getrealQuestionPaper'
    response = u_file.get_json(exam_list_url)
    exams = m_get(response, 'data')
    if m_get(response, 'result') != 0 or exams is None:
        log.error('request exam list error. response: {}'.format(response))
        return
    exam_infos = []
    log.info('request exam list success. exams size: {}'.format(len(exams)))
    for exam in exams:
        for sub_exam in m_get(exam, 'paperList'):
            exam_infos.append({
                'level': m_get(exam, 'level'),
                'title': m_get(sub_exam, 'title').replace('年-', '年真题-')
            })
    log.info('exam paper size: {}'.format(len(exam_infos)))
    for exam_info in exam_infos:
        log.info('--->begin download exam paper: {}-{}'.format(exam_info['level'], exam_info['title']))
        # 检查本地缓存试卷题目
        exam_question_cache_file = r'result\jiemo-exam\{}-{}.json'.format(exam_info['level'], exam_info['title'])
        u_file.ready_dir(exam_question_cache_file)
        if os.path.isfile(exam_question_cache_file):
            log.info('The exam question cache file is exist: {}'.format(exam_question_cache_file))
            continue

        response = requests.post(exam_question_url,
                                 data={'level': exam_info['level'], 'title': exam_info['title']},
                                 verify=False)
        if response.status_code != 200:
            log.error('request status code is not 200. code: {}'.format(response.status_code))
            continue
        response = json.loads(response.text)
        exam_questions = m_get(response, 'data')
        if m_get(response, 'result') != 0 or exams is None:
            log.error('request exam questions error. response: {}'.format(response))
            return
        log.info('get exam questions success. size: {}'.format(len(exam_questions)))
        u_file.cache_json(exam_questions, exam_question_cache_file)
        log.info('--->end download exam paper: {}-{}'.format(exam_info['level'], exam_info['title']))
    log.info('--->end crawler exam questions.')


if __name__ == '__main__':
    log.info('begin process')
    crawler_special_knowledge()
