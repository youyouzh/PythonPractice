#!/usr/bin/python
# -*- coding: UTF-8 -*-
import copy
import json
import os

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode

from u_base.u_file import get_abs_cache_path, covert_url_to_filename
from u_base.u_log import logger
from u_base import u_file, u_time

# 小米请求Cookie中相关的token，注意查询和创建不一样，token很容易过期
SERVICE_TOKEN = 'jNa2f6UlbQ0iiMIayebNzWXbJI4GNaJPy7rOg7Y6IYPaI2DcCQmORKDOFupsBVdJPrxYV8MuedxjUPAmFD3L1NOub6CBcZ0HJJDFC4VqGR0UFRdnlqpT+D8/SKXDZ6jMZC1RBUQc+Go4xk+fP04tkcw2kTh4AZkXnovgoDuW/amjybslBHttYMrT+kGPLAxL6tXkSPVpo5mzmYMDeHQepRWrwXR+DCPsJk0bz6ErmVyiXak6A3ElpdDzJ9iqYyyE+LpeWxjTMzHnpAC8yGLbjQMEQRFcGxkkLbqb3JyBebLCscelqhdI6vgAf3HH6alP0G+aEq+KWizNgcqz2LbweSF148YFDmv5/2inEhDFCYIZL+XlcvrjhMqTs5+SExLNc30xu1hKTgbw6FyptcQ0tg=='
SLH_TOKEN = 'x54e8StjpkJ+0AbsnECEPCHU4fw='
HEADERS = {
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://i.mi.com/note/h5',
    'Origin': 'https://i.mi.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Cookie': f'uLocale=zh_CN; iplocale=zh_CN; userId=140552443; i.mi.com_istrudev=true; i.mi.com_ph=ZiAu6BtEi2jFoJh8KnACvg==; i.mi.com_isvalid_servicetoken=true; serviceToken={SERVICE_TOKEN}; i.mi.com_slh={SLH_TOKEN}',
}
QUERY_FULL_NOTE_API = 'https://i.mi.com/note/full/page/'
CREATE_NOTE_API = 'https://i.mi.com/note/note'
FOLDER_MAP = {
    '名言名句': '40862048875725632',
    '岁月痕迹': '8688720070836832',
    '工作寄语': '8269417101525600',
    '心灵寄语': '8505051742863968',
    '梦境之尘': '8505051744698976',
    '段子': '8269417096282720',
    '灵忆': '8269626721305184',
    '简单事项记录': '8505051743650400',
}


def note_read():
    input_path = 'saved_resource.html'
    base_path = 'note'
    fin = open(input_path, 'r', encoding='UTF-8')
    # fout = open(output_path, 'w')
    note_html = fin.read()
    soup = BeautifulSoup(note_html, 'lxml')
    note_folds = soup.find_all('div', {'class': 'folder-brief'})   # 所有便笺文件夹列表
    i = 1
    for note_fold in note_folds:   # 遍历所以便签夹
        fold_name = note_fold.contents[0].string  # 便签夹名称
        if not fold_name:
            fold_name = note_fold.contents[0].contents[0].string
        # print('fold name: ' + str(fold_name.strip()))
        output_path = base_path + '/' + fold_name.strip() + '/'
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        fout_all = open(output_path + '0000.txt', 'w+', encoding='UTF-8')
        note_nodes = note_fold.find_all('div', {'class': 'note-brief'})   # 便签夹下的所有便签
        for note_node in note_nodes:
            date_node = note_node.find('span', {'class': 'modify-date'})  # 时间节点
            note_date = date_node.get('title')  # 详细的时间信息反正span便签的title中
            note_content_node = note_node.find('div', {'class': 'js_snippet'})  # 便签笔记内容节点
            note_content = ''
            for pic in note_content_node:    # 笔记节点是br标签分开的，所以要遍历内容
                if pic.name != 'br' and pic:
                    # print(pic.string.strip())
                    note_content += pic.string
            print('note date: ' + str(note_date), 'note content: ' + str(note_content))
            # 写入单个文件
            fout = open(output_path + str(i) + '.txt', 'w+', encoding='UTF-8')
            fout.write(str(note_date) + "\n")
            fout.write(str(note_content))
            fout.close()
            fout_all.write("\n\n" + str(note_date) + "\n")
            fout_all.write(str(note_content))
            i += 1
        fout_all.close()

    note_fold_out_nodes = soup.find_all('div', {'class': 'js_normal_note', 'data-folder-id': '0'})   # 没有进行分组的标签
    output_path = base_path + '/' + '未分组' + '/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    fout_all = open(output_path + '0000.txt', 'w+', encoding='UTF-8')
    for note_node in note_fold_out_nodes:
        date_node = note_node.find('span', {'class': 'modify-date'})  # 时间节点
        note_date = date_node.get('title')  # 详细的时间信息反正span便签的title中
        note_content_node = note_node.find('div', {'class': 'js_snippet'})  # 便签笔记内容节点
        note_content = ''
        for pic in note_content_node:  # 笔记节点是br标签分开的，所以要遍历内容
            if pic.name != 'br' and pic:
                # print(pic.string.strip())
                note_content += pic.string
        print('note date: ' + str(note_date), 'note content: ' + str(note_content))
        # 写入单个文件
        fout = open(output_path + str(i) + '.txt', 'w+', encoding='UTF-8')
        fout.write(str(note_date) + "\n")
        fout.write(str(note_content))
        fout.close()
        fout_all.write("\n\n" + str(note_date) + "\n")
        fout_all.write(str(note_content))
        i += 1
    fout_all.close()


def create_note(title: str, note_content: str, folder_id: str,
                note_create_mill_timestamp: int, note_update_mill_timestamp: int):
    entry = {
        'content': note_content,
        'colorId': 0,
        'folderId': folder_id,
        'createDate': note_create_mill_timestamp,
        'modifyDate': note_update_mill_timestamp,
        'extraInfo': '{"title":"' + title + '"}'
    }
    # 分隔符去掉空格
    entry = json.dumps(entry, separators=(',', ':'))
    data = {
        'entry': entry,
        'serviceToken': SERVICE_TOKEN
    }
    data = urlencode(data, encoding='utf-8')

    # header添加webForm格式
    create_headers = copy.deepcopy(HEADERS)
    create_headers['content-type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    response = requests.post(CREATE_NOTE_API, data=data, headers=create_headers)
    if response.status_code != 200:
        logger.error('request create note return code is not 200: {}'.format(response))
        return False
    result = json.loads(response.text)
    entry = u_file.m_get(result, 'data.entry')
    if 'code' not in result or result['code'] != 0 or not entry:
        logger.error('request create note return code fail: {}'.format(result))
        return False
    logger.info('create note success: {}'.format(entry))
    return entry


def get_full_notes(sync_tag: str = ''):
    """
    通过模拟请求获取所有小米便签中的笔记
    :param sync_tag: 下一页标识
    :return: 格式化后的小米笔记列表
    """
    format_notes = []
    note_cache_file = r'result\full_notes.json'

    # 迭代获取所有笔记列表
    while True:
        params = {
            'ts': u_time.get_now_mill_timestamp(),
            'syncTag': sync_tag,
            'limit': 200
        }
        logger.info('begin request notes from sync_tag: {}'.format(sync_tag))
        request_api = QUERY_FULL_NOTE_API + '?' + urlencode(params)
        cache_file = os.path.join(get_abs_cache_path(), covert_url_to_filename(QUERY_FULL_NOTE_API)
                                  + '-sync_tag=' + sync_tag)
        result = u_file.get_content_with_cache(request_api, headers=HEADERS, cache_file=cache_file)

        if not result:
            logger.error('request notes api fail.')
            break

        result = json.loads(result)
        notes = u_file.m_get(result, 'data.entries')
        if 'code' not in result or result['code'] != 0 or not notes:
            logger.error('request notes api result is not success: {}'.format(result))
            break

        # 提取下一页开始标识
        sync_tag = u_file.m_get(result, 'data.syncTag')
        logger.info('request notes api success. notes size: {}, next sync tag: {}'.format(len(notes), sync_tag))
        for note in notes:
            format_note = {
                'id': note['id'],
                'tag': note['tag'],
                'folder_id': note['folderId'],
                'create_time': note['createDate'],
                'modify_time': note['modifyDate'],
                'content': note['snippet'],
            }
            # 提取title
            if 'extraInfo' in note:
                format_note['title'] = json.loads(note['extraInfo']).get('title', '')
            format_notes.append(format_note)
        u_file.dump_json_to_file(note_cache_file, format_notes)
    return format_notes


if __name__ == '__main__':
    # note_read()
    # get_full_notes()
    create_note('test title', 'test content', FOLDER_MAP['简单事项记录'], 1707286416174, 1707286416174)
