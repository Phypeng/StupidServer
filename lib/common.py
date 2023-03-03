import sqlite3
import subprocess
import threading
import traceback

import error_code
import logging
import time
import functools

log_on = False


class RWLock(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.r_cond = threading.Condition(self.lock)
        self.w_cond = threading.Condition(self.lock)
        self.read_waiter = 0
        self.write_waiter = 0
        self.state = 0
        self.owners = []
        self.write_first = True

    def write_acquire(self, blocking=True):
        me = threading.get_ident()
        with self.lock:
            while not self._write_acquire(me):
                if not blocking:
                    return False

                self.write_waiter += 1
                self.w_cond.wait()
                self.write_waiter -= 1

        return True

    def _write_acquire(self, me):
        if self.state == 0 or (self.state < 0 and me in self.owners):
            self.state -= 1
            self.owners.append(me)
            return True

        if self.state > 0 and me in self.owners:
            raise RuntimeError('cannot recursively wrlock a rdlocked lock')

        return False

    def read_acquire(self, blocking=True):
        me = threading.get_ident()
        with self.lock:
            while not self._read_acquire(me):
                if not blocking:
                    return False

                self.read_waiter += 1
                self.r_cond.wait()
                self.read_waiter -= 1

        return True

    def _read_acquire(self, me):
        if self.state < 0:
            return False

        if not self.write_waiter:
            ok = True
        else:
            ok = me in self.owners

        if ok or not self.write_first:
            self.state += 1
            self.owners.append(me)
            return True

        return False

    def unlock(self):
        me = threading.get_ident()
        with self.lock:
            try:
                self.owners.remove(me)
            except ValueError:
                raise RuntimeError('cannot release un-acquired lock')

            if self.state > 0:
                self.state -= 1
            else:
                self.state += 1

            if not self.state:
                if self.write_waiter and self.write_first:
                    self.w_cond.notify()
                elif self.read_waiter:
                    self.r_cond.notify_all()
                elif self.write_waiter:
                    self.w_cond.notify()

    read_release = unlock
    write_release = unlock


def do_command(cmd, err_code=error_code.ERROR_INTERFACE_DO_COMMAND_ERROR):
    if log_on:
        logging.debug(cmd)
    err, res = subprocess.getstatusoutput(cmd)
    if err != 0:
        if log_on:
            logging.error('do_command cmd=%s err=%s res=%s err_code=%s'
                          % (cmd, err, res, error_code.ErrorException(err_code)))
        raise error_code.ErrorException(err_code)
    else:
        return res


class SQLite:
    def __init__(self, file='sqlite.db'):
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()


class ResultThread(threading.Thread):
    def __init__(self, func, args=()):
        super(ResultThread, self).__init__()
        self._func = func
        self._args = args
        self._result = None

    def run(self):
        self._result = self._func(*self._args)

    def get_result(self):
        return self._result


def time_tester(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('Calling %s() consumes %.3f s.' % (func.__name__, end - start))
        return result

    return wrapper


def set_interval(interval_seconds):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():
                try:
                    function(*args, **kwargs)
                except (Exception,):
                    if log_on:
                        logging.debug('\nCron Function Exception:%s\n' % traceback.format_exc())
                while not stopped.wait(interval_seconds):
                    try:
                        function(*args, **kwargs)
                    except (Exception,):
                        if log_on:
                            logging.debug('\nCron Function Exception:%s\n' % traceback.format_exc())

            t = threading.Thread(target=loop)
            t.daemon = True
            t.start()
            return stopped

        return wrapper

    return decorator
