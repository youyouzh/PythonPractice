import os
import u_base.u_log as log
import numpy as np


__all__ = ['point_file_to_matrix']


def point_file_to_matrix(path, delimiter):
    """
    读取数据文件并转换为矩阵吗，使用 np.loadtxt()代替
    :param path: 文件路径
    :param delimiter: 数据之间的分隔符
    :return: 矩阵
    """
    if not os.path.isfile(path):
        log.info("the file is not exist. path: %s" % path)
        return
    fout = open(path, "r")
    line = fout.readline().strip()
    values = [float(value) for value in line.split(delimiter)]
    matrix = np.array(values)
    while line:
        matrix = np.vstack((matrix, [float(value) for value in line.split(delimiter)]))
        line = fout.readline().strip()
    fout.close()
    return matrix
