"""
进程相关处理
"""

import os
import time
import psutil


def kill_pid(pid):
    """
    中止传入pid所对应的进程
    :param pid: 进程id
    :return:
    """
    if os.name == 'nt':
        # Windows系统
        cmd = 'taskkill /pid ' + str(pid) + ' /f'
        try:
            os.system(cmd)
            print(pid, 'killed')
        except Exception as e:
            print(e)
    elif os.name == 'posix':
        # Linux系统
        cmd = 'kill ' + str(pid)
        try:
            os.system(cmd)
            print(pid, 'killed')
        except Exception as e:
            print(e)
    else:
        print('Undefined os.name')


def write_current_pid(filepath='default.pid'):
    """
    将当前程序的经常id写入文件
    :return:
    """
    with open(filepath, mode='w') as fin:
        fin.write(os.getpid().__str__())


def read_pid_from_file(filepath='default.pid'):
    """
    从pid文件中读取进程id
    :param filepath:
    :return:
    """
    with open(filepath, mode='r') as fout:
        return fout.read()


def get_pid_from_process(proc_name):
    """
    便利进程列表，获取指定名称的进程id
    :return:
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == proc_name:
                return proc.pid
        except psutil.NoSuchProcess:
            pass
    return None


def restart_exe_process(proc_name):
    """
    管理某个进程，定时自动重启
    :param proc_name:
    :return:
    """
    time_counter = 0
    os.system(f'start {proc_name}.exe')
    print(f'start process: {proc_name}.exe')
    while True:
        time_counter += 1
        time.sleep(1)
        if time_counter == 1800:
            print('time counter attach.')
            pid = read_pid_from_file(f'{proc_name}.pid')
            kill_pid(pid)
            print(f'kill pid: {pid}')
            time.sleep(1)
            os.system(f'start {proc_name}.exe')
            print(f'restart {proc_name}.exe')
            time_counter = 0
