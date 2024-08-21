import os
import sys
import logging
import time
from logging import handlers

ROTATION = 0
INFINITE = 1


logger = logging.getLogger('uusama')
logger.DEBUG = logging.DEBUG
logger.INFO = logging.INFO
logger.WARNING = logging.WARNING
logger.ERROR = logging.ERROR
logger.CRITICAL = logging.CRITICAL


# log function, deprecate
debug = logger.debug
info = logger.info
warn = logger.warning
error = logger.error
critical = logger.critical


# 日志等级过滤
class MaxLevelFilter(logging.Filter):
    """Filters (lets through) all messages with level < LEVEL"""
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        # "<" instead of "<=": since logger.setLevel is inclusive, this should be exclusive
        return record.levelno < self.level


def get_log_path(name='log') -> str:
    # 初始化log
    log_path = os.path.join(os.getcwd(), 'log')
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    return os.path.join(log_path, name + time.strftime('-%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + '.log')


def config_file_logger(logging_instance, log_level, log_file, log_type=ROTATION,
                       max_size=1073741824, print_console=True, generate_wf_file=False):
    """
    config logging instance
    :param logging_instance: logger实例
    :param log_level: the log level
    :param log_file: log file path
    :param log_type:
        Two type: ROTATION and INFINITE

        log.ROTATION will let logfile switch to a new one (30 files at most).
        When logger reaches the 30th logfile, will overwrite from the
        oldest to the most recent.

        log.INFINITE will write on the logfile infinitely
    :param max_size: str max size
    :param print_console: Decide whether or not print to console
    :param generate_wf_file: Decide whether or not decide warning or fetal log file
    :return: none
    """
    # config object property
    logging_instance.setLevel(log_level)

    # '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
    # log format
    formatter = logging.Formatter(
        '%(levelname)s:\t %(asctime)s * '
        '[%(process)d:%(thread)x] [%(filename)s:%(lineno)s]\t %(message)s'
    )

    # print to console
    if print_console:
        # 避免默认basicConfig已经注册了root的StreamHandler，会重复输出日志，先移除掉
        for handler in logging.getLogger().handlers:
            if handler.name is None and isinstance(handler, logging.StreamHandler):
                logging.getLogger().removeHandler(handler)
        # DEBUG INFO 输出到 stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        stdout_handler.setLevel(log_level)
        stdout_handler.addFilter(MaxLevelFilter(logging.WARNING))

        # WARNING 以上输出到 stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr_handler.setLevel(max(log_level, logging.WARNING))

        logging_instance.addHandler(stdout_handler)
        logging_instance.addHandler(stderr_handler)

    # set RotatingFileHandler
    if log_type == ROTATION:
        rf_handler = handlers.RotatingFileHandler(log_file, 'a', max_size, 30, encoding='utf-8')
    else:
        rf_handler = logging.FileHandler(log_file, 'a', encoding='utf-8')

    rf_handler.setFormatter(formatter)
    rf_handler.setLevel(log_level)

    # generate warning and fetal log to wf file
    if generate_wf_file:
        # add warning and fetal handler
        file_wf = str(log_file) + '.wf'
        warn_handler = logging.FileHandler(file_wf, 'a', encoding='utf-8')
        warn_handler.setLevel(logging.WARNING)
        warn_handler.setFormatter(formatter)
        logging_instance.addHandler(warn_handler)

    logging_instance.addHandler(rf_handler)


default_log_path = get_log_path()
config_file_logger(logger, logging.INFO, default_log_path, print_console=True)


def set_log_level(level):
    """
    change log level during runtime
    :param level: log level
    :return: none
    """
    logger_instance = _LoggerInstance()
    logger_instance.getlogger().setLevel(level)


# 读取日志最后N行
def get_last_n_logs(num: int):
    """
    读取大文件的最后几行
    :param num: 读取行数
    :return:
    """
    num = int(num)
    blk_size_max = 4096
    n_lines = []
    with open(default_log_path, 'rb') as fp:
        fp.seek(0, os.SEEK_END)
        cur_pos = fp.tell()
        while cur_pos > 0 and len(n_lines) < num:
            blk_size = min(blk_size_max, cur_pos)
            fp.seek(cur_pos - blk_size, os.SEEK_SET)
            blk_data = fp.read(blk_size)
            assert len(blk_data) == blk_size
            lines = blk_data.split(b'\n')

            # adjust cur_pos
            if len(lines) > 1 and len(lines[0]) > 0:
                n_lines[0:0] = lines[1:]
                cur_pos -= (blk_size - len(lines[0]))
            else:
                n_lines[0:0] = lines
                cur_pos -= blk_size
            fp.seek(cur_pos, os.SEEK_SET)

    if len(n_lines) > 0 and len(n_lines[-1]) == 0:
        del n_lines[-1]

    last_lines = []
    for line in n_lines[-num:]:
        last_lines.append(line.decode('utf-8'))
    return last_lines


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


if __name__ == '__main__':
    logger.debug('test log debug.')
    logger.info('test log info')
    logger.info('test log info 中文')

    logger.warning('test log warning')
    logger.error('test log error')
