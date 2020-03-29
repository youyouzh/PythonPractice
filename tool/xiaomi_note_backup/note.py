#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
from bs4 import BeautifulSoup


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

if __name__ == '__main__':
    note_read()

