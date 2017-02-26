import logging
import sys

default_format = "%(asctime)s|%(filename)s:%(line_no)d|%(funcName)s %(message)s"
default_name = "Home"


class DefaultLogger(logging.Logger):
    def __init__(self, name, level=logging.INFO, fmt=default_format):
        logging.Logger.__init__(self, name, level)
        handler = logging.FileHandler(name + ".log", "a")
        handler.formatter = logging.Formatter(fmt=fmt)
        self.addHandler(handler)

    def debug(self, msg, *args, **kwargs):
        kwargs["line_no"] = sys._getframe(1).f_lineno
        logging.Logger.debug(self, msg, *args, extra=kwargs)

    def error(self, msg, *args, **kwargs):
        kwargs["line_no"] = sys._getframe(1).f_lineno
        logging.Logger.error(self, msg, *args, extra=kwargs)

    def info(self, msg, *args, **kwargs):
        kwargs["line_no"] = sys._getframe(1).f_lineno
        logging.Logger.info(self, msg, *args, extra=kwargs)


Log = DefaultLogger(default_name, level=logging.INFO)