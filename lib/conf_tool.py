import configparser
import threading
from lib.common import RWLock


# 相同构造参数的单例基类
class SingletonMeta(type):
    _instances = {}
    _args_set = set()

    def __call__(cls, *args, **kwargs):
        with threading.Lock():
            if cls not in cls._instances or args not in cls._args_set:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
                cls._args_set.add(args)
            res = cls._instances[cls]
        return res


class ConfTool(metaclass=SingletonMeta):
    def __init__(self, path):
        self.rw_lock = RWLock()
        self.path = path
        self.cf = configparser.ConfigParser()
        self.reload()

    def reload(self):
        try:
            self.rw_lock.write_acquire()
            self.cf.read(self.path, encoding='utf-8')
        finally:
            self.rw_lock.write_release()

    def get(self, field, key):  # 获取字符串类型的选项值
        try:
            self.rw_lock.read_acquire()
            result = self.cf.get(field, key)
        except (Exception,):
            return ""
        finally:
            self.rw_lock.read_release()
        return result

    def set(self, field, key, value):
        try:
            self.rw_lock.write_acquire()
            self.cf.set(field, key, value)
            self.cf.write(open(self.path, 'w'))
        except (Exception,) as e:
            print(e)
            return False
        finally:
            self.rw_lock.write_release()
        return True


http_conf = ConfTool('./http_conf.ini')
