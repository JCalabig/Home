import logging
import sys, os

default_format = "%(asctime)s|%(file_name)s:%(line_no)d|%(funcName)s %(message)s"
default_name = "Home"


class DefaultLogger(logging.Logger):
    def __init__(self, name, level=logging.INFO, fmt=default_format):
        logging.Logger.__init__(self, name, level)
        handler = logging.FileHandler(name + ".log", "a")
        handler.formatter = logging.Formatter(fmt=fmt)
        self.addHandler(handler)
        self.addHandler(logging.StreamHandler())

    def debug(self, msg, *args, **kwargs):
        rec = self._get_caller_info()
        logging.Logger.debug(self, msg, *args, extra=rec, **kwargs)

    def error(self, msg, *args, **kwargs):
        rec = self._get_caller_info()
        logging.Logger.error(self, msg, *args, extra=rec, **kwargs)

    def info(self, msg, *args, **kwargs):
        rec = self._get_caller_info()
        logging.Logger.info(self, msg, *args, extra=rec, **kwargs)

    @staticmethod
    def _get_caller_info():
        caller_info = sys._getframe(2)
        return {
            "line_no": caller_info.f_lineno,
            "file_name": os.path.basename(caller_info.f_code.co_filename)
        }


Log = DefaultLogger(default_name, level=logging.INFO)
