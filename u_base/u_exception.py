#!/usr/bin/python
# -*- coding: utf-8 -*
# custom exception


__all__ = [
    'UBaseException', 'DecoratorException', 'LoggerException',
    'ResException', 'NoSuchProcess', 'AccessDenied', 'NetworkException',
    'AsyncMsgError', 'ThreadTermException', 'LockFileError',
    'NotImplementedYet', 'ConfigError'
]


class UBaseException(Exception):
    """
    base Exception. All other Exceptions will inherit this.
    """

    def __init__(self, msg):
        self._msg = 'Base module Exception:' + str(msg)

    def __str__(self):
        return repr(self._msg)


# ## Decorator Exceptions ####
class DecoratorException(UBaseException):
    """
    DecoratorException
    """

    def __init__(self, msg):
        super(self.__class__, self).__init__(msg)


# ## Log related exceptions ####
class LoggerException(UBaseException):
    """
    Exception for logging, especially for u_log
    """

    def __init__(self, msg):
        super(self.__class__, self).__init__(msg)


# ## Resource related exceptions ####
class ResException(UBaseException):
    """
    Resource related Exception
    """

    def __init__(self, msg):
        UBaseException.__init__(self, msg)


class NoSuchProcess(ResException):
    """
    No such Process Exception
    """

    def __init__(self, pid, str_process_name):
        ResException.__init__(self, 'NoSuchProcess, pid %d, process name:%s' % (pid, str_process_name))


class AccessDenied(ResException):
    """
    Resource Access Denied Exception
    """

    def __init__(self, str_resource):
        ResException.__init__(self, 'Resource access denied: %s' % str_resource
                              )


# ## Net related exceptions ####
class NetworkException(UBaseException):
    """
    Network related Exception
    """

    def __init__(self, msg=''):
        UBaseException.__init__(self, msg)


class AsyncMsgError(NetworkException):
    """
    async msg related Exception
    """

    def __init__(self, msg=''):
        NetworkException.__init__(self, msg)


# ## Shell related exceptions ####
class ShellException(UBaseException):
    """
    Exception for shell
    """

    def __init__(self, msg=''):
        UBaseException.__init__(self, msg)


class IOException(UBaseException):
    """
    IO related exceptions
    """

    def __init__(self, msg=''):
        UBaseException.__init__(self, msg)


class NoSuchFileOrDir(IOException):
    """
    No such file or directory Exception
    """

    def __init__(self, msg=''):
        IOException.__init__(self, msg)


class ThreadTermException(UBaseException):
    """
        Thread termination error
    """

    def __init__(self, msg=''):
        UBaseException.__init__(self, msg)


class NotInitialized(UBaseException):
    """
    Not initialized yet
    """

    def __init__(self, msg=''):
        msg = 'Not initialized: %s' % msg
        UBaseException.__init__(self, msg)


class LockFileError(UBaseException):
    """
    LockFileError
    """

    def __init__(self, msg=''):
        msg = 'LockFileError: %s' % msg
        UBaseException.__init__(self, msg)


class ExpectFailure(UBaseException):
    """
    Expect failure for unittest
    """

    def __init__(self, expect, got):
        msg = 'expect failure, expect {0}, got {1}'.format(expect, got)
        UBaseException.__init__(self, msg)


class NotImplementedYet(UBaseException):
    """
    Not implemented yet
    """

    def __init__(self, msg=''):
        msg = 'The functionality is not implemented yet, {0}'.format(msg)
        UBaseException.__init__(self, msg)


class ConfigError(UBaseException):
    """
    ConfigError
    """

    def __init__(self, msg=''):
        msg = 'Configuration Error: {0}'.format(msg)
        UBaseException.__init__(self, msg)
