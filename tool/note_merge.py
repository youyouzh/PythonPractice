"""
处理所有在手机上记录的日记之类的内容
"""
import os
from datetime import datetime
from u_base import u_log as log
from u_base import u_file


def process_xiaomi_notes():
    note_dir = r'G:\AAZZlong\可爱的人生\便签\note'

    tag_dirs = os.listdir(note_dir)
    notes = []
    log.info('tag size: {}'.format(len(tag_dirs)))
    for tag_dir in tag_dirs:
        tag_path = os.path.join(note_dir, tag_dir)
        note_paths = os.listdir(tag_path)
        log.info('tag: {}, note size: {}'.format(tag_dir, len(note_paths)))
        for note_filename in note_paths:
            if '0000.txt' in note_filename:
                continue

            note_path = os.path.join(tag_path, note_filename)
            with open(note_path, 'r', encoding='utf-8') as file_handler:
                line = file_handler.readline()
                content = ''
                note_date_time = None
                line_index = -1
                while line:
                    line_index += 1
                    # 过滤空行
                    if not line:
                        continue
                    # 包含4个空格的为内容，否则为时间
                    if '    ' in line:
                        # 内容去掉前面是个空格
                        content += line.replace('    ', '')
                    if not note_date_time and '年' in line:
                        note_date_time = datetime.strptime(line.strip(), '%Y年%m月%d日 %H:%M')
                    line = file_handler.readline()

                if not note_date_time:
                    log.error('note date time is empty. note_path: {}'.format(note_path))
                    continue

                notes.append({
                    'tag': tag_dir,
                    'title': '',
                    'time': note_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': content
                })
    log.info('process xiaomi notes success. size: {}'.format(len(notes)))
    return notes


def process_samsung_notes():
    note_dir = r'G:\AAZZlong\可爱的人生\便签\Samsung-Backup\三星S8笔记'

    tag_dirs = os.listdir(note_dir)
    notes = []
    log.info('tag size: {}'.format(len(tag_dirs)))
    for tag_dir in tag_dirs:
        tag_path = os.path.join(note_dir, tag_dir)

        note_paths = os.listdir(tag_path)
        log.info('tag: {}, note szie: {}'.format(tag_dir, len(note_paths)))
        for note_filename in note_paths:
            note_names = note_filename.replace('.txt', '').split('_')
            if len(note_names) < 3:
                log.warn('The file is unknown note name: {}'.format(note_filename))
            note_title = note_names[0] if note_names[0] != 'Notes' else ''
            note_date_time_str = '20' + note_names[1] + note_names[2]
            note_date_time = datetime.strptime(note_date_time_str, '%Y%m%d%H%M%S')
            note_path = os.path.join(tag_path, note_filename)
            note_content = u_file.read_content(note_path)
            notes.append({
                'tag': tag_dir,
                'title': note_title,
                'time': note_date_time.strftime('%Y-%m-%d %H:%M:%S'),
                'content': note_content
            })
    log.info('process samsung notes finish. size: {}'.format(len(notes)))
    return notes


if __name__ == '__main__':
    notes = process_xiaomi_notes()
    notes.extend(process_samsung_notes())
    u_file.dump_json_to_file(r'result\notes.json', notes)
