#!/usr/bin/python
# -*- coding: utf-8 -*
# log function

"""
:description:
    common log related module
"""
from __future__ import print_function

__all__ = [
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'MIN_LEVEL',
    'init_log_instance', 'set_log_level', 'logger',
    'ROTATION', 'INFINITE',
    're_init_log_instance', 'get_inited_logger_name', 'parse_log_line',
]

import os
import re
import sys
import logging
import time
import threading
from logging import handlers

from u_base import u_exception
from u_base import u_platform

ROTATION = 0
INFINITE = 1

# log rotation count
ROTATION_COUNTS = 30

# log level
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
MIN_LEVEL = logging.DEBUG

# global logging instance name
G_INITED_LOGGER = []

# log function, deprecate
debug = logging.debug
info = logging.info
warn = logging.warning
error = logging.error
critical = logging.critical


class _Singleton(object):
    """
    internal use for logging.
    """
    _LOCK = threading.Lock()

    def __init__(self, cls):
        self.__instance = None
        self.__cls = cls

    def __call__(self, *args, **kwargs):
        self._LOCK.acquire()
        if self.__instance is None:
            self.__instance = self.__cls(*args, **kwargs)
        self._LOCK.release()
        return self.__instance


# 日志等级过滤
class MaxLevelFilter(logging.Filter):
    """Filters (lets through) all messages with level < LEVEL"""
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        # "<" instead of "<=": since logger.setLevel is inclusive, this should be exclusive
        return record.levelno < self.level


@_Singleton
class _LoggerInstance(object):
    """
    logger Instance object, for singleton
    """
    _logger_instance = None
    _max_size = 0
    _log_file = ''
    _log_type = ROTATION
    _print_console = False

    def __init__(self):
        pass

    def get_logger(self) -> logging.Logger:
        """
        get logger instance
        :return: logger instance
        """
        if self._logger_instance is None:
            raise u_exception.LoggerException(
                'The logger has not been initialized Yet. '
                'Call init_log_instance first'
            )
        return self._logger_instance

    def set_logger(self, logger):
        """
        set the logger instance
        :param logger: logging instance
        :return: none
        """
        if self._logger_instance is not None:
            raise u_exception.LoggerException(
                """WARNING!!! The logger instance has been initialized already\
                .Please do NOT set twice, or call reset_log_instance replace""")
        self._logger_instance = logger

    def reset_logger(self, logger):
        """
        reset logging instance
        :param logger: logger instance
        :return: none
        """
        del self._logger_instance
        self._logger_instance = logger
        logging.root = logger

    def is_initialized(self):
        """
        judge the log instance is Initialized or not
        :return: True or False
        """
        return self._logger_instance is not None

    def config_file_logger(self, log_level, log_file, log_type,
                           max_size, print_console=True, generate_wf_file=False):
        """
        config logging instance
        :param log_level: the log level
        :param log_file: log file path
        :param log_type: log type
        :param max_size: str max size
        :param print_console: Decide whether or not print to console
        :param generate_wf_file: Decide whether or not decide warning or fetal log file
        :return: none
        """
        # if not log file path, create dir
        if not os.path.exists(log_file):
            try:
                os.mknod(log_file)
            except IOError:
                # create exception
                raise u_exception.LoggerException(
                    'log file does not exist. '
                    'try to create it. but file creation failed'
                )

        # config object property
        self._log_file = log_file
        self._log_type = log_type
        self._logger_instance.setLevel(log_level)
        self._max_size = max_size
        self._print_console = print_console

        # '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
        # log format
        formatter = logging.Formatter(
            '%(levelname)s:\t %(asctime)s * '
            '[%(process)d:%(thread)x] [%(filename)s:%(lineno)s]\t %(message)s'
        )

        # print to console
        if print_console:
            logging.info('print_console enabled, will print to stdout')
            # 避免默认basicConfig已经注册了root的StreamHandler，会重复输出日志，先移除掉
            for handler in self._logger_instance.handlers:
                if handler.name is None and isinstance(handler, logging.StreamHandler):
                    self._logger_instance.removeHandler(handler)
            # DEBUG INFO 输出到 stdout
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setFormatter(formatter)
            stdout_handler.setLevel(min(log_level, MIN_LEVEL))
            stdout_handler.addFilter(MaxLevelFilter(WARNING))

            # WARNING 以上输出到 stderr
            stderr_handler = logging.StreamHandler(sys.stderr)
            stderr_handler.setFormatter(formatter)
            stderr_handler.setLevel(max(log_level, WARNING))

            self._logger_instance.addHandler(stdout_handler)
            self._logger_instance.addHandler(stderr_handler)

        # set RotatingFileHandler
        rf_handler = None
        if log_type == ROTATION:
            rf_handler = handlers.RotatingFileHandler(self._log_file, 'a', max_size, ROTATION_COUNTS, encoding='utf-8')
        else:
            rf_handler = logging.FileHandler(self._log_file, 'a', encoding='utf-8')

        rf_handler.setFormatter(formatter)
        rf_handler.setLevel(log_level)

        # generate warning and fetal log to wf file
        if generate_wf_file:
            # add warning and fetal handler
            file_wf = str(self._log_file) + '.wf'
            warn_handler = logging.FileHandler(file_wf, 'a', encoding='utf-8')
            warn_handler.setLevel(logging.WARNING)
            warn_handler.setFormatter(formatter)
            self._logger_instance.addHandler(warn_handler)

        self._logger_instance.addHandler(rf_handler)


def init_log_instance(name, level=logging.INFO, file='u_log', log_type=ROTATION,
                      max_size=1073741824, print_console=False, generate_wf=False) -> logging.Logger:
    """
    Initialize your logging
    :param name: Unique logger name
    :param level: 4 default levels: log.DEBUG log.INFO log.ERROR log.CRITICAL
    :param file: log file. Will try to create it if no existence
    :param log_type:
        Two type: log.ROTATION and log.INFINITE

        log.ROTATION will let logfile switch to a new one (30 files at most).
        When logger reaches the 30th logfile, will overwrite from the
        oldest to the most recent.

        log.INFINITE will write on the logfile infinitely
    :param max_size: max log size with byte, default 1GB
    :param print_console: print to stdout or not?
    :param generate_wf: print log msg with level >= WARNING to file (${logfile}.wf)
    :return: none
    *E.g.*
    ::
        import logging
        from cup import log
        log.init_comlog(
            'test',
            log.DEBUG,
            '/home/work/test/test.log',
            log.ROTATION,
            1024,
            False
        )
        log.info('test xxx')
        log.critical('test critical')
    """
    logging_instance = _LoggerInstance()
    if not logging_instance.is_initialized():
        # initialize logging instance
        logging_instance.set_logger(logging.getLogger())

        # create log file
        if os.path.exists(file) is False:
            # create file on linux platform
            if u_platform.is_linux():
                os.mknod(file)
            elif u_platform.is_windows():
                with open(file, 'w+') as log_file_handle:
                    log_file_handle.write('---Windows Log File Creation ---\n')
            else:
                raise u_exception.LoggerException("not support platform\n")
        elif os.path.isfile(file) is False:
            raise u_exception.LoggerException('The log file exists. But it\'s not regular file\n')

        # set log config
        logging_instance.config_file_logger(level, file, log_type, max_size, print_console, generate_wf)
        logging.info('-' * 20 + 'Log Initialized Successfully' + '-' * 20)
        # set global log name
        global G_INITED_LOGGER
        G_INITED_LOGGER.append(name)
    else:
        print('init_log_instance has been already initialized')
    return logging_instance.get_logger()


def re_init_log_instance(name, level=logging.INFO, file='u_log', log_type=ROTATION,
                         max_size=1073741824, print_console=False, generate_wf=False) -> logging.Logger:
    """
    re initialize logging system, parameters same to initLogInstance.
    re_init_log_instance will reset all logging parameters，
    Make sure you used a different logger name from the old one!
    """
    global G_INITED_LOGGER
    if name in G_INITED_LOGGER:
        msg = 'logger name:%s has been already initialized!!!' % name
        raise ValueError(msg)

    logging_instance = _LoggerInstance()
    logging_instance.reset_logger(logging.getLogger(name))
    # create log file
    if os.path.exists(file) is False:
        # create file on linux platform
        if u_platform.is_linux():
            os.mknod(file)
        elif u_platform.is_windows():
            with open(file, 'w+') as log_file_handle:
                log_file_handle.write('---Windows Log File Creation ---\n')
        else:
            raise u_exception.LoggerException("not support platform\n")
    elif os.path.isfile(file) is False:
        raise u_exception.LoggerException('The log file exists. But it\'s not regular file\n')

    # set log config
    G_INITED_LOGGER.append(name)
    logging_instance.config_file_logger(level, file, log_type, max_size, print_console, generate_wf)
    logging.info('-' * 20 + 'Log Reinitialized Successfully' + '-' * 20)
    return logging_instance


def get_inited_logger_name():
    """
    get initialized logger name
    """
    global G_INITED_LOGGER
    return G_INITED_LOGGER


def parse_log_line(log_line: str):
    """
    return a dict if the line is valid.
    Otherwise, return None
    ::
        dict_info:= {
           'loglevel': 'DEBUG',
           'date': '2015-10-14',
           'time': '16:12:22,924',
           'pid': 8808,
           'tid': 1111111,
           'srcline': 'util.py:33',
           'msg': 'this is the log content'
        }
    :param log_line: log line
    """
    try:
        content = log_line[log_line.find(']'):]
        content = content[(content.find(']') + 1):]
        content = content[(content.find(']') + 1):].strip()
        regex = re.compile('[ \t]+')
        items = regex.split(log_line)
        log_level, date, time_, _, pid_tid, src = items[0:6]
        pid, tid = pid_tid.strip('[]').split(':')
        return {
            'level': log_level.strip(':'),
            'date': date,
            'time': time_,
            'pid': pid,
            'tid': tid,
            'line': src.strip('[]'),
            'msg': content
        }
    except Exception:
        return {}


def log_file_func_info(msg: str, depth=0):
    """return log traceback info"""
    temp_msg = ' * [%s:%s] [%s:%s] ' % (
        os.getpid(), threading.current_thread().ident,
        os.path.basename(sys._getframe(depth + 3).f_code.co_filename),
        sys._getframe(depth + 3).f_lineno
    )
    return '{0}{1}'.format(temp_msg, msg)


def set_log_level(level):
    """
    change log level during runtime
    :param level: log level
    :return: none
    """
    logger_instance = _LoggerInstance()
    logger_instance.getlogger().setLevel(level)


def init_default_log(name='root'):
    # 初始化log
    log_path = os.path.join(os.getcwd(), 'log')
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    time_str = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_path = os.path.join(log_path, f'{name}-{time_str}.log')
    return init_log_instance(name, INFO, log_path, print_console=True)


def run_logging():
    logging.debug('中文')
    init_log_instance('test', INFO, './test.log', print_console=True)
    # test call init_log_instance twice
    init_log_instance('test', INFO, './test.log', print_console=True)

    # test log diff log level
    logging.info('test log info')
    logging.debug('test log debug')
    logging.info('中文')
    logging.error('test log error. {id}'.format(id=12))

    re_init_log_instance(
        're-test', INFO, './re.test.log',
        ROTATION, 102400000, True
    )
    logging.info('re:test info')
    logging.debug('re:test debug')
    logging.debug('re:中文')


logger: logging.Logger = init_default_log()


if __name__ == '__main__':
    logger.debug('test log debug.')
    logger.info('test log info')
    logger.info('test log info 中文')

    logger.warning('test log warning')
    logger.error('test log error')
