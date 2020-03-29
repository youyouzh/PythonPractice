# -*- coding:utf-8 -*-
import os
import os.path


# 删除指定文件夹（绝对路径），递归删除
def remove_dir(path):
    if not os.listdir(path):  # 空文件夹直接删除
        os.rmdir(path)
        return True
    for dir in os.listdir(path):
        full_dir = os.path.join(path, dir)
        if os.path.isdir(full_dir):   # 判断是否为文件加
            if not os.listdir(full_dir):  # 空文件夹直接删除
                os.rmdir(full_dir)
            else:  # 非空文件夹则遍历
                remove_dir(full_dir)
        else:  # 文件则直接删除
            os.remove(full_dir)


def file_move(source_path, target_path, delete_move_path=False, cut_str=''):
    """
    将指定文件夹下的所有子文件夹中的文件移动到指定目录
    用于解压缩之后分散的文件
    source_path: 待处理的目录
    target_path: 所有文件移动到的目录，
    delete_move_path: 是否删除遍历完的文件夹
    cut_str: 需要剪切的文件名
    """
    target_path = os.path.abspath(target_path)  # 获取绝对路径
    if not os.path.exists(target_path):
        print("create target path: %s" % target_path)
        os.makedirs(target_path)
    source_path = os.path.abspath(source_path)
    dir_list = os.listdir(source_path)
    for filename in dir_list:
        full_filename = os.path.join(source_path, filename)  # 还原完整路径
        if os.path.isdir(full_filename):
            print('child path: ' + full_filename)
            file_move(full_filename, target_path)
        else:
            # if os.path.exists(os.path.join(root_path, filename[0:cut_length])):
            #     rename_filename = filename[0:cut_length] + '0'
            rename = filename.replace(cut_str, '')  # 替换掉文件末尾
            rename = os.path.join(target_path, rename)
            if not os.path.exists(rename):  # 如果文件存在则不进行移动
                print('move ' + full_filename + ' to ' + os.path.join(target_path, filename))
                os.rename(full_filename, os.path.join(rename))  # 通过重命名实现移动文件
        if delete_move_path and os.path.isdir(full_filename):  # 删除遍历完的文件夹
            remove_dir(full_filename)
    return True


def file_list(source_path):
    """
    列出文件夹下的所有文件
    :param source_path: 源文件夹
    :return:
    """
    if not os.path.exists(source_path):
        print("The source path is not exist" % source_path)
        return
    for filename in os.listdir(source_path):
        print(filename)


if __name__ == '__main__':
    # project_path = 'E:/www/dgc_sdkops_platform/front/trunk'
    # code_pass(project_path)
    source_path = r'D:\data\word-gif\主题词书爬虫gifs_1127缩略图'
    target_path = r'D:\data\word-gif\image\thumbnail'
    # print("begin move file: from %s -> %s" % (source_path, target_path))
    # file_move(source_path, target_path)
    file_list(target_path)
