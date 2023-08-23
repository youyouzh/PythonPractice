import os
import sys
import logging
import time
from logging import handlers

ROTATION = 0
INFINITE = 1


logger = logging.getLogger()


def init_default_log(name='log-'):
    # 初始化log
    log_path = os.path.join(os.getcwd(), 'log')
    if not os.path.isdir(log_path):
        os.makedirs(log_path)
    log_path = os.path.join(log_path, name + time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time())) + '.log')
    config_file_logger(logger, logging.INFO, log_path, print_console=True)


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

        # WARNING 以上输出到 stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        stderr_handler.setLevel(max(log_level, logging.WARNING))

        logging_instance.addHandler(stdout_handler)
        logging_instance.addHandler(stderr_handler)

    # set RotatingFileHandler
    rf_handler = None
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


init_default_log()
