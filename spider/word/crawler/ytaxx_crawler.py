import os
import time
from u_base import u_log as log
from u_base import u_file
from u_base.u_file import m_get


def download_exam_questions():
    """
    从羊驼日语单词app下载真题题目列表json数据
    目前只有N1-N3三个等级的题库，缺少部分年份题目
    :return:
    """
    n_levels = [1, 2, 3]
    for n_level in n_levels:
        log.info('--->begin download exam question. category: N{}真题'.format(n_level))
        exam_list_url = 'http://vocabulary.ytaxx.com/api/exam/getExamList?category={}'.format(n_level - 1)
        response = u_file.get_json(exam_list_url)
        if m_get(response, 'code') != 0 or m_get(response, 'data') is None:
            log.error('request exam list error. category: N{}真题'.format(n_level))
            continue
        exams = m_get(response, 'data', [])
        log.info('request category exams success. exam size: {}'.format(len(exams)))

        for exam in exams:
            # 检测真题已经下载过则跳过
            exam_cache_file = r'result\yt-exam\N{}-{}-{}-json'.format(n_level, exam['examName'], exam['id'])
            u_file.ready_dir(exam_cache_file)
            if os.path.isfile(exam_cache_file):
                log.info('The exam questions is downloaded. id: {}, name: {}'.format(exam['id'], exam['examName']))
                continue

            # 下载真题json，并保存到本地文件
            log.info('begin download exam question. exam name: {}'.format(exam['examName']))
            exam_question_url = 'http://vocabulary.ytaxx.com/api/exam/questions?examId={}'.format(exam['id'])
            response = u_file.get_json(exam_question_url)
            if m_get(response, 'code') != 0 or m_get(response, 'data') is None:
                log.error('request exam questions error. category: N{}真题'.format(n_level))
                continue
            questions = response['data'][0]['questionList']
            exam['question'] = questions
            log.info('request exam question success. question size: {}'.format(len(questions)))
            u_file.cache_json(exam, exam_cache_file)
            time.sleep(0.2)
        log.info('--->end download exam question. category: N{}真题'.format(n_level))


if __name__ == '__main__':
    log.info('begin process')
    download_exam_questions()
