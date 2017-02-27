import logging
import sys, os

default_format = "%(asctime)s|%(file_name)s:%(line_no)d|%(funcName)s %(message)s"
default_name = "Home"


class DefaultLogger(logging.Logger):
    def __init__(self, name, level=logging.INFO, fmt=default_format):
        logging.Logger.__init__(self, name, level)
        self._filename = name + ".log"
        self._delete_file()
        self._formatter = fmt
        self._handler = None
        self.addHandler(logging.StreamHandler())
        self.create_file_handler()

    def create_file_handler(self):
        self._handler = logging.FileHandler(self._filename, "a")
        self._handler.formatter = logging.Formatter(fmt=self._formatter)
        self.addHandler(self._handler)

    def _delete_file(self):
        if os.path.isfile(self._filename) and os.path.exists(self._filename):
            os.remove(self._filename)

    def delete_file_handler(self):
        if self._handler is None:
            return
        self._handler.close()
        self.removeHandler(self._handler)
        self._handler = None

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
