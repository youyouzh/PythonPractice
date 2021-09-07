#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import re
import os
from bs4 import BeautifulSoup
import u_base.u_file as u_file
import u_base.u_log as log

# global config
config = {
    'begin_article': 0,      # 开始扫描的文章数，便于继续扫描
    'max_article': 10,       # 扫描的最大文章数
    'console_output': True,  # 是否控制台输出d
    'template_input_html': 'page/template.html',  # 输入HTML路径，控制显示样式
    'output_html_path': 'page/output.html',    # 输出HTML路径，空则不输出
    'output_json_path': 'page/result.json',    # 输出json路径，空则不输出
}
CRAWL_HOST = 'https://www.qingwk.com'
IMAGE_HOST = 'https://img.qingwk.com/'
COURSE = [
    {
        'name': '动漫插画班',
        'url': 'https://www.qingwk.com/school/dongman'
    },
    {
        'name': '二次元插画班',
        'url': 'https://www.qingwk.com/school/erciyuan'
    },
    {
        'name': '日系插画精品-商业',
        'url': 'https://www.qingwk.com/school/shangyejuese'
    },
    {
        'name': '动漫厚涂班',
        'url': 'https://www.qingwk.com/school/dmht'
    },
]


def extract_init_json_data(html_content: str) -> dict:
    """
    匹配html中的初始化json数据
    :param html_content: html内容
    :return: json字典
    """
    # 返回结果通过js处理成document，只能正则匹配
    pattern = re.compile(r'__INITIAL_STATE__=(.+);\(function')
    search_content = re.search(pattern, html_content)
    if search_content is None:
        log.error('Can not match any data.')
        return {}
    init_json = search_content.group(1)
    json_data = json.loads(init_json)
    return json_data


def get_question_url(question_id) -> str:
    return CRAWL_HOST + '/coach/subject/' + str(question_id) + '-good-1.html'


def extract_dict_field(source_dict, fields):
    extract_dict = {}
    for key in source_dict:
        if key in fields:
            extract_dict[key] = source_dict[key]
    return extract_dict


def get_course_info_by_html(course_url: str) -> list:
    """
    爬取每一个步骤的课程信息，通过html解析
    :param course_url: 课程地址
    :return: 课程信息列表
    """
    cache_file = r'cache\course-step-info.html'
    html_content = u_file.get_cache_content(course_url, cache_file)
    soup = BeautifulSoup(html_content, 'lxml')

    # find the step url
    course_step_infos = []
    level_item_a_nodes = soup.select('div.level-item > a')
    for level_item_a_node in level_item_a_nodes:
        level_image_node = level_item_a_node.select('div.level-img')
        course_step_infos.append({
            'url': CRAWL_HOST + level_item_a_node['href'],
            'cover_image_url': '',
            'step': level_item_a_node.select('p.level-name')[0].string,
            'title': level_item_a_node.select('p.level-title')[0].string,
            'description': level_item_a_node.select('p.level-txt')[0].string
        })
    log.info('extract course step info success. size: {}'.format(len(course_step_infos)))
    return course_step_infos


def get_course_info(course_url: str) -> dict:
    """
    爬取课程信息
    :param course_url: 课程url
    :return: 课程信息
    """
    cache_file = r'cache\course-info.html'
    html_content = u_file.get_cache_content(course_url, cache_file, use_cache=False)

    # 返回结果通过js处理成document，只能正则匹配
    json_data = extract_init_json_data(html_content)
    class_detail = json_data['school']['classDetail']

    # 阶段作业，字段： id, name, summary, coverImageUrl
    stage_works = class_detail['classCreations']
    for stage_work in stage_works:
        stage_work['url'] = get_question_url(stage_work['id'])

    keep_course_fields = ['id', 'name', 'navImageUrl', 'coverImageUrl', 'description', 'summary', 'validDays', 'buyCount']
    course_info = extract_dict_field(class_detail['learnClass'], keep_course_fields)
    course_info['stageWorks'] = stage_works

    stage_courses = []
    keep_stage_course_fields = ['id', 'courseId', 'courseName', 'simpleName', 'summary', 'courseImageUrl',
                                'stageId', 'teacherName', 'ValidDayCount']
    for stages in class_detail['learnClass']['stages']:
        for stage in stages['courses']:
            stage_course = extract_dict_field(stage, keep_stage_course_fields)
            stage_course['url'] = CRAWL_HOST + '/course/detail/' + str(stage_course['courseId'])
            stage_course['stageName'] = stages['name']
            stage_course['stageValidDays'] = stages['validDays']
            stage_course['stageSummary'] = stages['summary']
            stage_courses.append(stage_course)
    course_info['stageCourses'] = stage_courses
    return course_info


def get_stage_course_info(stage_course_url: str) -> dict:
    """
    提取课程每个步骤详情页的作业题目信息和课程等信息
    :param stage_course_url: 每个步骤课程详情页
    :return: 作业题目信息
    """
    cache_file = r'cache\course-step-info.html'
    html_content = u_file.get_cache_content(stage_course_url, cache_file)

    # 返回结果通过js处理成document，只能正则匹配
    json_data = extract_init_json_data(html_content)
    questions = json_data['coach']['subjectList']
    log.info('question size: {}'.format(len(questions)))

    # extract question_infos
    question_infos = []
    keep_question_fields = ['id', 'name', 'title', 'tip', 'summary', 'url', 'files', 'questionCount']
    for question in questions:
        question_info = extract_dict_field(question, keep_question_fields)
        question_info['url'] = get_question_url(question['id'])
        question_infos.append(question_info)

    # extract chapter infos
    chapter_infos = json_data['course']['detail']['chapters']
    return {
        'questions': question_infos,
        'chapters': chapter_infos
    }


def get_question_detail(question_detail_url: str) -> dict:
    """
    获取题目详情页面的题目详情信息
    :param question_detail_url: 题目详情页面url
    :return: 题目详情数据
    """
    cache_file = r'cache\course-question-info.html'
    html_content = u_file.get_cache_content(question_detail_url, cache_file)

    json_data = extract_init_json_data(html_content)
    question_detail = json_data['coach']['subject']
    # 'subjectQuestionPage',
    keep_fields = ['id', 'title', 'summary', 'tip', 'name', 'keywords', 'previousId', 'nextId',
                   'courseId', 'questionCount', 'description', 'content', 'files']
    question_info = extract_dict_field(question_detail, keep_fields)
    return question_info


def get_video_notes(period_id: int) -> list:
    params = {
        '_ts_': '1621612527891',
        'periodId': str(period_id),
        'index': '1'
    }
    response = u_file.get_json('https://rt.qingwk.com/course/note/list', params=params)
    if 'data' not in response or 'datas' not in response['data']:
        log.error('The response has not notes')
        return []
    log.info('pageCount: {}, rowCount: {}'.format(response['data']['pageCount'], response['data']['rowCount']))
    notes = response['data']['datas']
    log.info('notes count: {}'.format(len(notes)))
    return notes


def begin_crawl(course_url: str, tag: str = 'default'):
    course_info = get_course_info(course_url)
    for stage_course in course_info['stageCourses']:
        stage_course_info = get_stage_course_info(stage_course['url'])

        # 题目详情
        for question_info in stage_course_info['questions']:
            question_detail_info = get_question_detail(question_info['url'])
            question_info['detail'] = question_detail_info
        stage_course['questions'] = stage_course_info['questions']  # 题目列表
        stage_course['chapters'] = stage_course_info['chapters']    # 直播课列表
    u_file.dump_json_to_file(r'cache\course-info-' + tag + '.json', course_info)
    return course_info


def crawl_courses(name=None):
    for course_config in COURSE:
        if name is None or course_config['name'] == name:
            begin_crawl(course_config['url'], course_config['name'])


def output_course_list(course_data_path: str):
    course_info = u_file.load_json_from_file(course_data_path)

    template = u_file.read_content(r'cache/template.html')
    html_content = '<ul>\n'
    for stage_course in course_info['stageCourses']:
        html_content += '<li>' + stage_course['courseName']

        # 如果有题目的话，列出题目
        questions = stage_course['questions']
        if len(questions) > 0:
            html_content += '\n<ul>'
            for question in questions:
                # question_detail_content = question['detail']['content']
                html_content += '<li>' + question['name'] + '---' + question['summary'] + '\n'
            html_content += '</ul>'
        html_content += '</li>\n'
    html_content += '</ul>'
    template = template.replace('{{title}}', course_info['name'])
    template = template.replace('{{content}}', html_content)
    u_file.write_content(r'cache\output.html', template)


def output_course_question(name):
    course_data_path = r'cache\course-info-{}.json'.format(name)
    course_info = u_file.load_json_from_file(course_data_path)

    template = u_file.read_content(r'cache/template.html')
    html_content = ''
    for stage_course in course_info['stageCourses']:
        html_content += '<h1><a href="{}" target="_blank">{}</a></h1>\n'\
            .format(stage_course['url'], stage_course['courseName'])

        # 如果有题目的话，列出题目
        questions = stage_course['questions']
        if len(questions) > 0:
            for question in questions:
                # question_detail_content = question['detail']['content']
                html_content += '<h4><a href="{}" target="_blank">{}</a></h4>\n'\
                    .format(question['url'], question['title'])
                # html_content += question['detail']['content']

    template = template.replace('{{title}}', course_info['name'])
    template = template.replace('{{content}}', html_content)
    u_file.write_content(r'cache\output-title-{}.html'.format(name), template)


def output_course_chapter_notes(name):
    course_data_path = r'cache\course-info-{}.json'.format(name)
    course_info = u_file.load_json_from_file(course_data_path)

    content = '# {}\n\n'.format(name)
    log.info('stage_course size: {}'.format(len(course_info['stageCourses'])))
    for stage_course in course_info['stageCourses']:
        chapters = stage_course['chapters']
        content += '## {}\n\n'.format(stage_course['courseName'])
        log.info('course {} chapters size: {}'.format(stage_course['courseName'], len(chapters)))
        if len(chapters) <= 0:
            continue

        # 遍历每一章节
        for chapter in chapters:
            content += '\n### {}\n\n'.format(chapter['name'])

            periods = chapter['periods']
            log.info('chapter: {}, periods size: {}'.format(chapter['name'], len(periods)))
            if len(periods) <= 0:
                continue

            # 遍历每个视频讲解
            for period in periods:
                # 获取笔记并保存
                content += '\n#### {}\n\n'.format(period['name'])
                notes = get_video_notes(period['id'])
                log.info('period: {}, notes size: {}'.format(period['name'], len(notes)))
                if len(notes) <= 0:
                    log.info('The period: {}, notes is empty.'.format(period['name']))
                    continue

                for note in notes:
                    if len(note['content']) <= 5:
                        log.info('The not is short: {}'.format(note['content']))
                        continue
                    content += note['content'] + '\n---------{}\n'.format(note['likeNum'])
        u_file.write_content(r'cache\output-note-{}.md'.format(name), content)
    u_file.write_content(r'cache\output-note-{}.md'.format(name), content)


if __name__ == '__main__':
    # get_course_info(course_home_url)
    # get_question_infos(step_home_url)
    # get_question_detail(question_home_url)
    # name =  '动漫插画班', '二次元插画班', '日系插画精品-商业', '动漫厚涂班',
    output_course_chapter_notes('动漫插画班')
    # course_names = ['动漫插画班', '二次元插画班', '日系插画精品-商业', '动漫厚涂班']
    # for course_name in course_names:
    #     # crawl_courses(course_name)
    #     output_course_question(course_name)
