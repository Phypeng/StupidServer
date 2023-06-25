import os
import sys
import importlib
import traceback
import inspect
from functools import lru_cache, cmp_to_key
from types import FunctionType, ModuleType
import logging

from error_code import ErrorException, ERROR_INTERFACE_CHECK_MATCH_RULE, ERROR_INTERFACE_IMPORT_INTERFACE, \
    ERROR_INTERFACE_NO_SUCH_MATCH_RULE, ERROR_INTERFACE_MATCH_RULE_EXISTED, OP_SUCCEEDED, ERROR_INTERFACE_UNKNOWN
from lib.common import RWLock


def reload_package(package):
    assert (hasattr(package, "__package__"))
    assert isinstance(package.__package__, str)

    fn = package.__file__
    fn_dir = os.path.join(os.path.dirname(fn) + os.sep)
    module_visit = {fn}
    del fn

    def reload_recursive_ex(module):
        importlib.reload(module)

        for module_child in vars(module).values():
            if isinstance(module_child, ModuleType):
                module_tmp = module_child
            else:
                module_tmp = inspect.getmodule(module_child)

            fn_child = getattr(module_tmp, "__file__", None)

            if (fn_child is not None) and fn_child.startswith(fn_dir):
                if fn_child not in module_visit:
                    module_visit.add(fn_child)
                    reload_recursive_ex(module_tmp)

    return reload_recursive_ex(package)


@lru_cache(maxsize=500, typed=True)
def rule_split(rule_str: str):
    return rule_str.split('/')


@lru_cache(maxsize=1000, typed=True)
def path_split(path_str: str):
    return path_str.split('/')


@lru_cache()
def check_match_rule(match_rule: str) -> bool:
    """
    校验规则:
        0.以 '/' 开头
        1.不能以 '/' 结尾
        2.占位符只支持 '{}' 与 '*',前者匹配单个参数,后者匹配前缀.
        注:占位符前后不能有除 '/' 之外的字符,否则不进行匹配,如下列情况,后两种不进行匹配
            /dock/{}/status/{}              ok
            /dock/{}/*                      ok
            /dock/user{}/status/{}log       no
            /dock/user*                     no
        注:/reload 的 POST 方法已被占用,用于重新加载接口
    """
    if match_rule[0] != '/':
        return False

    if match_rule[-1] == '/':
        return False

    rule_arr = rule_split(match_rule)

    for index in range(len(rule_arr)):
        key = rule_arr[index]
        if '{}' in key and '{}' != key:
            break

        if '*' in key:
            if '*' == key:
                if index != len(rule_arr) - 1:
                    break
            else:
                break

    return True


@lru_cache()
def compare_match_rule(path_x: str, path_y: str):
    """
    按过滤规则排序
          0,以 '/' 分割 match-rule, 越长的优先级越高
          1,相同位置的,绝对匹配 > 参数匹配 > 前缀匹配
    """

    """
    降序排列
        x < y return 1
        x > y return -1
        x = y return 0
    """

    if path_x == path_y:
        return 0

    rule_arr_x = rule_split(path_x)
    rule_arr_y = rule_split(path_y)

    if len(rule_arr_x) != len(rule_arr_y):
        return -1 if len(rule_arr_x) > len(rule_arr_y) else 1

    rule_size = len(rule_arr_x)
    for index in range(rule_size):
        key_x = rule_arr_x[index]
        key_y = rule_arr_y[index]

        if key_x == '{}':
            if key_y == '{}':
                if index == rule_size - 1:
                    return 0
                else:
                    continue
            elif key_y == '*':
                return 1 if index != (rule_size - 1) else -1
            else:
                return 1
        elif key_x == '*':
            if key_y == '{}':
                return 1 if index == (rule_size - 1) else -1
            elif key_y == '*':
                if index == rule_size - 1:
                    return 0
                else:
                    continue
            else:
                return 1 if index == (rule_size - 1) else 0
        else:
            if key_y == '{}':
                return -1
            elif key_y == '*':
                if index == rule_size - 1:
                    return -1
                else:
                    continue
            else:
                if index == rule_size - 1:
                    return 0
                else:
                    continue


def match_interface_by_path(match_rule: str, real_path: str) -> bool:
    rule_arr = rule_split(match_rule)
    path_arr = path_split(real_path)

    rule_size = len(rule_arr)
    path_size = len(path_arr)

    if rule_size > path_size:
        return False

    for index in range(rule_size):
        key = rule_arr[index]
        if key == '{}':
            if index == rule_size - 1:
                return index == path_size - 1
            else:
                continue
        elif key == '*':
            if index == rule_size - 1:
                return True
            else:
                return path_arr[index] == rule_arr[index]
        else:
            if path_arr[index] != rule_arr[index]:
                return False

            if index == rule_size - 1:
                if index == path_size - 1:
                    return True
                else:
                    return False
            else:
                continue


class InterfaceManager:
    """
    路径匹配模式 -- 只匹配,不负责解析传参
      绝对匹配:
          /path/status:
              /path/status        yes
              /path/stat          no
              /path/              no
              /path               no
              /path/status/       no
              /path/status/log    no
      参数匹配:
          /path/{}
              /path/user0         yes
              /path/user1         yes
              /path               no
              /path/user1/file0   no
      前缀匹配:
          /path/*
              /path/user0         yes
              /path/user0/file0   yes
              /path               no
    遵循 最长路径优先 规则。当路径长度相同时，继而遵循 绝对匹配 > 参数匹配 > 前缀匹配 的规则。
    """
    __rw_lock = RWLock()
    __interface_dir_path = ''
    __interface_list = []

    def __init__(self, interface_dir_path: str):
        self.__interface_dir_path = interface_dir_path

    def list_interface(self):
        self.__rw_lock.read_acquire()
        interface_list = []
        try:
            for interface in self.__interface_list:
                interface_list.append(interface[0])
        finally:
            self.__rw_lock.read_release()

        return interface_list

    def reload_interface(self):
        reload_result = []
        # [{
        #     "status":0,
        #     "msg":"Operation-succeeded",
        #     "traceback":""
        #     "data":{
        #         "interface_file":"test_c",
        #         "match_rule":""
        #     }
        # }, ...]

        try:
            if self.__interface_dir_path not in sys.path:
                sys.path.append(self.__interface_dir_path)

            lib_dic = {}

            # 获取路径
            for top, dirs, not_dirs in os.walk(self.__interface_dir_path, topdown=False):
                if top == self.__interface_dir_path:
                    for item in not_dirs:
                        item_arr = item.split(".")
                        if len(item_arr) != 2:
                            continue
                        if item_arr[1] != "py":
                            continue

                        try:
                            model_filename = f"{os.path.basename(self.__interface_dir_path)}.{item_arr[0]}"
                            lib = importlib.import_module(model_filename)

                            reload_package(lib)
                        except (BaseException,):
                            ee = ErrorException(ERROR_INTERFACE_IMPORT_INTERFACE)
                            print(traceback.format_exc())
                            reload_result.append({
                                "status": ee.get_code(),
                                "msg": ee.get_msg(),
                                "traceback": traceback.format_exc(),
                                "data": {
                                    "interface_file": item_arr[0],
                                    "match_rule": None}
                            })
                            continue

                        if lib is None:
                            continue

                        if hasattr(lib, 'match_rule') and isinstance(lib.match_rule, str):
                            lib.match_rule = lib.match_rule.strip()
                            if isinstance(getattr(lib, 'interface_function', None), FunctionType):
                                if not check_match_rule(lib.match_rule):
                                    ee = ErrorException(ERROR_INTERFACE_CHECK_MATCH_RULE)
                                    reload_result.append({
                                        "status": ee.get_code(),
                                        "msg": ee.get_msg(),
                                        "traceback": None,
                                        "data": {
                                            "interface_file": item_arr[0],
                                            "match_rule": lib.match_rule}
                                    })
                                else:
                                    if lib.match_rule in lib_dic:
                                        ee = ErrorException(ERROR_INTERFACE_MATCH_RULE_EXISTED)
                                        reload_result.append({
                                            "status": ee.get_code(),
                                            "msg": ee.get_msg(),
                                            "traceback": None,
                                            "data": {
                                                "interface_file": item_arr[0],
                                                "match_rule": lib.match_rule}
                                        })
                                    else:
                                        lib_dic[lib.match_rule] = lib
                                        ee = ErrorException(OP_SUCCEEDED)
                                        reload_result.append({
                                            "status": ee.get_code(),
                                            "msg": ee.get_msg(),
                                            "traceback": None,
                                            "data": {
                                                "interface_file": item_arr[0],
                                                "match_rule": lib.match_rule}
                                        })
                        else:
                            ee = ErrorException(ERROR_INTERFACE_NO_SUCH_MATCH_RULE)
                            print(lib)
                            reload_result.append({
                                "status": ee.get_code(),
                                "msg": ee.get_msg(),
                                "traceback": None,
                                "data": {
                                    "interface_file": item_arr[0],
                                    "match_rule": None}
                            })
        except(BaseException,):
            logging.error(traceback.format_exc())
            ee = ErrorException(ERROR_INTERFACE_UNKNOWN)
            reload_result.append({
                "status": ee.get_code(),
                "msg": ee.get_msg(),
                "traceback": traceback.format_exc(),
                "data": {
                    "interface_file": None,
                    "match_rule": None}
            })
        else:
            match_rule_list = list(lib_dic.keys())
            match_rule_list.sort(key=cmp_to_key(compare_match_rule))

            self.__rw_lock.write_acquire()
            try:
                self.match_interface.cache_clear()
                self.__interface_list.clear()
                for match_rule in match_rule_list:
                    self.__interface_list.append((match_rule, lib_dic[match_rule]))
            finally:
                self.__rw_lock.write_release()
        finally:
            return reload_result

    @lru_cache(maxsize=500, typed=True)
    def match_interface(self, real_path: str):
        self.__rw_lock.read_acquire()
        m = None
        try:
            for interface in self.__interface_list:
                if match_interface_by_path(interface[0], real_path):
                    m = getattr(interface[1], 'interface_function', None)
                    break
        finally:
            self.__rw_lock.read_release()

        return m
