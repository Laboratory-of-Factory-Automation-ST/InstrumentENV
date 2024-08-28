import logging
from enum import Enum
import sys
from io import StringIO

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class Exceptable:
    def __init__(self, context):
        self.__context = context
        self.__exception = None
    
    def __enter__(self):
        try:
            self.__context.__enter__()
        except Exception as e:
            self.__exception = e
        return self
    
    def __exit__(self, except_type, except_val, except_trace):
        self.__context.__exit__(except_type, except_val, except_trace)
        return True
    
    @property
    def context(self):
        return self.__context
    
    @property
    def exception(self):
        return self.__exception
    
    def evaluate(self):
        if isinstance(self.exception, Exception):
            raise self.exception
        else:
            return self.context

class LogConfig(type):
    class LogLevel(Enum):
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR
        CRITICAL = logging.CRITICAL

    def __set_loglevel(cls, lvl: LogLevel):
        logging.getLogger().setLevel(level=lvl.value)
        match lvl:
            case cls.LogLevel.DEBUG:
                logging.debug("\n")
            case cls.LogLevel.INFO:
                logging.info("\n")
            case cls.LogLevel.WARNING:
                logging.warning("\n")
            case cls.LogLevel.ERROR:
                logging.error("\n")
            case cls.LogLevel.CRITICAL:
                logging.critical("\n")
    def __set_stream(cls, stream: StringIO):
        logging.basicConfig(stream=stream)
    
    SET_LOGLEVEL = property(None, __set_loglevel)
    SET_LOGSTREAM = property(None, __set_stream)

class Config(object, metaclass=LogConfig):
    SET_LOGSTREAM = sys.stderr
    SET_LOGLEVEL = LogConfig.LogLevel.WARNING
    __STDERR = sys.stderr
    __CAPTUREDERR = StringIO()

    def __new__(cls):
        sys.stderr = cls.__CAPTUREDERR

    def __del__(cls):
        sys.stderr = cls.__STDERR