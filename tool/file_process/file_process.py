# -*- coding:utf-8 -*-
import os
import os.path


def get_file_path(root_path, file_list, dir_list):
    # 获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        # 获取目录或者文件的路径
        dir_file_path = os.path.join(root_path, dir_file)
        # 判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            # 递归获取所有文件和目录的路径
            get_file_path(dir_file_path, file_list, dir_list)
        else:
            file_list.append(dir_file_path)
    return file_list


def file_through_1(root_path):
    result_files = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            result_files.append(os.path.join(root, file))
    return result_files


if __name__ == '__main__':
    root_path = r'G:\漫画\ps-sai扩展工具\sai笔刷和材质-uu\blotmap'
    result = file_through_1(root_path)
    for file in result:
        print(file[len(root_path):])
