import sys
import time


class SfdcLogger():
    _QUIET = 0
    _ERRORS = 1
    _WARNINGS = 2
    _INFO = 3
    _DEBUG = 4

    def __init__(self, level=_INFO):
        self._level = level
        self._ts_started = time.time()
        self._ts_last_logged = self._ts_started

    def _log(self, level, msg):
        ts = time.time()
        print("[%.2f][%.2f][%s] %s" % (
            ts - self._ts_started,
            ts - self._ts_last_logged,
            level,
            msg)
        )
        sys.stdout.flush()
        self._ts_last_logged = ts

    def err(self, msg):
        if self._level >= SfdcLogger._ERRORS:
            self._log("ERR", msg)

    def wrn(self, msg):
        if self._level >= SfdcLogger._WARNINGS:
            self._log("WRN", msg)

    def inf(self, msg):
        if self._level >= SfdcLogger._INFO:
            self._log("INF", msg)

    def dbg(self, msg):
        if self._level >= SfdcLogger._DEBUG:
            self._log("DBG", msg)
