#!/usr/bin/python
# -*- coding: utf-8 -*
"""
:desc:
    unittest module, some assert function
"""
import hashlib
import os
import sys
import traceback

from u_base import u_log
from u_base import u_exception

__all__ = [
    'assert_true',
    'assert_false',
    'assert_eq',
    'assert_not_eq',
    'assert_eq_one',
    'assert_lt',
    'assert_gt',
    'assert_ge',
    'assert_le',
    'assert_ne',
    'CUTCase',
    'CCaseExecutor',
    'expect_raise'
]


def _log_message(message):
    """
    log assert message
    :param message: message
    """
    try:
        u_log.backtrace_critical(message, 3)
    except Exception:
        pass


def _assert_bool(actual, expected, message=''):
    """
    assert bool, value should be exp (either True or False)
    :param actual: actual value
    :param expected: expected value
    :param message: append message
    :return:
    """
    if actual is not expected:
        msg = 'got {0}, expect {1}\nUser ErrMsg: {2}'.format(actual, expected, message)
        _log_message(message)
        assert False, msg


def assert_true(actual, message=''):
    """
    If actual value is not True, assert False and print to stdout.
    :param actual: actual value
    :param message: info log message
    :return:
    """
    if not isinstance(actual, bool):
        raise TypeError('The type of val is not bool')
    _assert_bool(actual, True, message)


def assert_false(actual, message=''):
    """
    If actual value is not False, assert False and print to stdout.
    :param actual: actual value
    :param message: info log message
    :return:
    """
    """
    val should be False. Assert False otherwise.
    """
    if not isinstance(actual, bool):
        raise TypeError('The type of val is not bool')
    _assert_bool(actual, False, message)


def assert_eq(actual, expected, message=''):
    """
    Assert actual value is equal to expected, otherwise assert False and print message
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    :return:
    """
    if actual != expected:
        message = 'got {0}, expect {1}\nUser ErrMsg: {2}'.format(actual, expected, message)
        _log_message(message)
        assert False, message


def assert_not_eq(actual, expected, message=''):
    """
    Assert actual value is not equal to expected, otherwise assert False and print message
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    :return:
    """
    if actual == expected:
        message = 'got {0} which is equal, expect not equal \nUser ErrMsg: {1}'.format(actual, message)
        _log_message(message)
        assert False, message


def assert_eq_one(actual, array, message=''):
    """
    assert actual equals one of the items in the [array]
    :param actual: actual value
    :param array: array value
    :param message: additional message
    :return:
    """
    equal = False
    str_arr = ''
    for i in array:
        str_arr += '|' + str(i) + '|'
        if i == actual:
            equal = True
            break
    if not equal:
        message = 'got {0}, expect one in the array: {1}\nUser ErrMsg: {2}'.format(actual, str_arr, message)
        _log_message(message)
        assert False, message


def assert_in(actual, array, message=''):
    """
    The same as to assert_eq_one, for backward compatibility
    :param actual: actual value
    :param array: array value
    :param message: additional message
    :return:
    """
    """
    same to assert_eq_one, for backward compatibility
    """
    assert_eq_one(actual, array, message)


def assert_not_in(actual, iterables, message=''):
    """
    Assert actual value is not equal any item in [iterables (e.g. a list)]
    :param actual: actual value
    :param iterables: iterables object, e.g. a list
    :param message: additional message
    :return:
    """
    """
    assert val not equal any item in [iteratables (e.g. a list)]
    """
    if actual in iterables:
        assert False, 'val :%s in iteratables. ErrMsg:%s' % (actual, message)


def assert_lt(actual, expected, message=''):
    """
    assert_lt, expect val < exp
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    """
    if actual >= expected:
        message = 'got {0}, expect less than {1}\nUser ErrMsg:{2}'.format(actual, expected, message)
        _log_message(message)
        assert False, message


def assert_gt(actual, expected, message=''):
    """
    assert_gt, expect val > exp
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    """
    if actual <= expected:
        message = 'got {0}, expect greater than {1}\nUser ErrMsg: {2}'.format(actual, expected, message)
        _log_message(message)
        assert False, message


def assert_ge(actual, expected, message=''):
    """
    expect val >= exp
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    """
    if actual < expected:
        message = ('got {0}, expect greater than (or equal to) {1}\nUser ErrMsg:{2}'.format(actual, expected, message))
        _log_message(message)
        assert False, message


def assert_le(actual, expected, message=''):
    """
    expect val <= exp
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    """
    if actual > expected:
        message = 'got {0}, expect less than (or equal to) {1}\nUser ErrMsg:{2}'.format(actual, expected, message)
        _log_message(message)
        assert False, message


def assert_ne(actual, expected, message=''):
    """
    expect val != exp
    :param actual: actual value
    :param expected: expected value
    :param message: additional message
    """
    if actual == expected:
        message = 'Expect non-equal, got two equal values' \
              '{0}:{1}\nUser Errmsg:{2}'.format(actual, expected, message)
        _log_message(message)
        assert False, message


def assert_boundary(actual, low, high, message=None):
    """
    expect low <= val <= high
    :param actual: actual value
    :param low: lower value
    :param high: higher value
    :param message: additional message
    :return:
    """
    if actual < low:
        message = 'Expect low <= val <= high, but val:{0} < low:{1}, msg:{2}'.format(actual, low, message)
        assert False, message
    if actual > high:
        message = 'Expect low <= val <= high, but val:%s > high:%s, msg:%s' % (actual, high, message)
        assert False, message


def _get_md5_hex(src_file):
    """
    get md5 hex string of a file
    :param src_file: file path
    :return:
    """
    with open(src_file, 'rb') as fhandle:
        md5obj = hashlib.md5()
        while True:
            strtmp = fhandle.read(131072)  # read 128k
            if len(strtmp) <= 0:
                break
            md5obj.update(strtmp.encode('utf-8'))
    return md5obj.hexdigest()


def assert_local_file_eq(source_file, target_file, message=''):
    """
    expect same md5 value of the two files
    :param source_file: source file path
    :param target_file: target file path
    :param message: additional message
    :return:
    """
    """
    expect same md5 value of the two files
    """
    assert os.path.exists(source_file)
    assert os.path.isfile(source_file)
    assert os.path.exists(target_file)
    assert os.path.isfile(target_file)
    source_md5 = _get_md5_hex(source_file)
    target_md5 = _get_md5_hex(target_file)
    message = 'expect same md5 value. source:%s, target:%s, errmsg:%s' % (source_md5, target_md5, message)
    assert source_md5 == target_md5, message


def assert_startswith(source, comp):
    """
    If source does NOT start with comp, assert False
    :param source:
    :param comp:
    :return:
    """
    message = 'expect source:{0} starts with:{1}'.format(source, comp)
    if not source.startswith(comp):
        assert False, message


def assert_none(source):
    """
    assert source is None
    :param source:
    :return:
    """
    if source is not None:
        assert False, 'expect source is None, but now is {0}'.format(source)


def expect_raise(func, exception, *argc, **kwargs):
    """
    assert the function will raise exception
    :param func: execute function
    :param exception: exception type
    :param argc: source func list parameters
    :param kwargs: source func dict parameters
    """
    try:
        func(*argc, **kwargs)
        raise u_exception.ExpectFailure(exception, None)
    except exception:
        pass


class CUTCase(object):
    """
    CUTCase is compatible with nosetests. You can inherit this class
    and implement your own TestClass.

    Notice class method [set_result] will set case status to True/False after
    executing the case. Then you can get case status in teardown through
    calling class method [get_result]
    """

    def __init__(self, logfile='./test.log', log_stdout=False, is_debug=False):
        """
        :param logfile:
            will invoke log.init_log_instance to initialize logging in order to
            support invoking logging functions log.info/debug/warn
        :param log_stdout:
            print to stdout or not
        :param is_debug:
            enable debug mode or not.
            If enabled, log level will be set to log.DEBUG.
            log.INFO (log level) will be set by default.
        """
        self._result = False
        if is_debug:
            debuglevel = u_log.DEBUG
        else:
            debuglevel = u_log.INFO

        u_log.init_log_instance(
            'test_case', debuglevel,
            logfile, u_log.ROTATION, 5242880, log_stdout
        )

    def setup(self):
        """
        set up
        """
        pass

    def test_run(self):
        """
        test_run function
        """
        pass

    def set_result(self, b_result):
        """
        set case running status
        """
        self._result = b_result

    def get_result(self):
        """
        get case status during case teardown
        """
        return self._result

    def teardown(self):
        """
        teardown
        """
        pass


class CCaseExecutor(object):
    """
    Executor class for executing CUTCase test cases. See the example below

    ::

        #!/usr/bin/env python

        import sys
        import os
        import logging

        import cup
        import sb_global

        from nfsinit import CClearMan
        from nfs import CNfs
        from cli import CCli

        class TestMyCase(cup.unittest.CUTCase):
            def __init__(self):
                super(self.__class__, self).__init__(
                    logfile=sb_global.G_CASE_RUN_LOG,
                    b_logstd=False
                )
                cup.log.info( 'Start to run ' + str(__file__ ) )
                self._cli = CCli()
                self._nfs = CNfs()
                self._uniq_strman = cup.util.CGeneratorMan()
                self._clearman = CClearMan()

            def setup(self):
                str_uniq = self._uniq_strman.get_uniqname()
                self._workfolder = os.path.abspath(os.getcwd()) \
                    + '/' + str_uniq
                self._work_remote_folder = \
                    self._nfs.translate_path_into_remote_under_rw_folder(
                    str_uniq
                    )
                os.mkdir(self._workfolder)
                self._clearman.addfolder(self._workfolder)

            def _check_filemd5(self, src, dst):
                ret = os.system('/usr/bin/diff --brief %s %s' % (src, dst) )
                cup.unittest.assert_eq( 0, ret )

            def test_run(self):
                #
                # @author: maguannan
                #
                inited_bigfile = sb_global.G_NFS_DISK_RD + \
                    sb_global.G_TEST_BIGFILE
                bigfile = self._workfolder + \
                    '/test_big_file_offsite_write_random_write'
                self.tmpfile = sb_global.G_TMP4USE + \
                    '/test_big_file_offsite_write_random_write'
                os.system( 'cp %s %s' % (inited_bigfile, bigfile) )
                os.system( 'cp %s %s' % (bigfile, self.tmpfile) )
                times = 50
                baseOffsite = 1000
                fp0 = open(bigfile, 'r+b')
                fp1 = open(self.tmpfile, 'rb+')
                for i in range( 0, times ):
                    fp0.seek(baseOffsite)
                    fp1.seek(baseOffsite)
                    fp0.write( 'a' * 100 )
                    fp1.write( 'a' * 100 )
                    baseOffsite += 1000
                fp0.close()
                fp1.close()

                self._check_filemd5(bigfile, self.tmpfile)

            def teardown(self):
                if self.get_result():
                    # if case succeeded, do sth
                    os.unlink(self.tmpfile)
                    self._clearman.teardown()
                else:
                    # if case failed, do sth else.
                    print 'failed'
                cup.log.info( 'End running ' + str(__file__ ) )

        if __name__ == '__main__':
            cup.unittest.CCaseExecutor().runcase(TestMyCase())
    """

    @classmethod
    def runcase(cls, case):
        """
        run the case
        """
        failed = False
        try:
            case.setup()
            case.test_run()
            case.set_result(True)
        # pylint: disable=W0703
        except Exception:
            print(traceback.format_exc())
            case.set_result(False)
            failed = True
        # case.teardown()
        if failed:
            try:
                case.fail_teardown()
            # pylint: disable=W0703
            except Exception:
                pass
            print('========================')
            print('======== Failed ========')
            print('========================')
            sys.exit(-1)
        case.teardown()
        print('========================')
        print('======== Passed ========')
        print('========================')
