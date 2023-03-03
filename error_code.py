ERROR_SERVICE = (-4, 'ERROR-SERVICE')  # 服务发生错误
ERROR_SERVICE_FATAL = (-3, 'FATAL-SERVICE')  # 发生致命错误,无法提供任何服务
ERROR_SERVICE_INTERFACE = (-2, 'INTERFACE-ERROR')  # 接口发生未被捕获的的错误
ERROR_SERVICE_INTERFACE_NOT_FOUND = (-1, 'INTERFACE-NOTFOUND')  # 接口未找到
OP_SUCCEEDED = (0, 'Operation-succeeded')  # 操作成功

ERROR_INTERFACE_PARAM = (3200, 'PARAM-ERROR')  # 接口参数错误
ERROR_INTERFACE_METHOD = (3201, 'METHOD-ERROR')  # 接口方法错误
ERROR_INTERFACE_DO_COMMAND_ERROR = (3202, 'DO-COMMAND-ERROR')  # 接口执行脚本发生错误
ERROR_INTERFACE_DIR_NOT_FOUND = (3603, 'DIR-NOT-FOUND')  # 接口目录未找到
ERROR_INTERFACE_CONTENT_TYPE = (3604, 'INTERFACE-CONTENT-TYPE-ERROR')  # 接口内容类型错误
ERROR_INTERFACE_REQUEST_JSON_INVALID = (3605, 'REQUEST-JSON-INVALID')  # 请求JSON格式错误
ERROR_INTERFACE_UNKNOWN_COMMAND = (3606, 'REQUEST-UNKNOWN-COMMAND')  # 请求中的命令未知
ERROR_INTERFACE_UNKNOWN_OPERATION = (3607, 'REQUEST-UNKNOWN-OPERATION')  # 请求中的操作类型未知

ERROR_INTERFACE_NOT_INIT = (3622, 'SERVICE-NOT-INIT')  # 服务未初始化完成,缺少运行的必备信息
ERROR_INTERFACE_PASSWORD = (3623, 'PASSWORD-INVALID')  # 口令无效
ERROR_INTERFACE_HTTP = (3626, 'HTTP-ERROR')  # HTTP 错误

ERROR_INTERFACE_CHECK_MATCH_RULE = (3627, 'CHECK-MATCH-RULE-ERROR')
ERROR_INTERFACE_IMPORT_INTERFACE = (3628, 'IMPORT-INTERFACE-ERROR')
ERROR_INTERFACE_NO_SUCH_MATCH_RULE = (3629, 'NO-SUCH-MATCH-RULE')
ERROR_INTERFACE_MATCH_RULE_EXISTED = (3630, 'MATCH-RULE-EXISTED')
ERROR_INTERFACE_UNKNOWN = (3631, 'INTERFACE-UNKNOWN-ERROR')
ERROR_INTERFACE_NOT_FINISHED = (3632, 'REQUEST-NOT-FINISHED')

__code_dic = {}
__msg_dic = {}

for __value in dict(globals()).values():
    if isinstance(__value, tuple) and len(__value) == 2 and isinstance(__value[0], int) and isinstance(__value[1], str):
        assert __value[0] not in __code_dic, f'{__value[0]} Already In DIC'
        assert __value[1] not in __msg_dic, f'{__value[1]} Already In DIC'
        __code_dic[__value[0]] = __value
        __msg_dic[__value[1]] = __value


def err_by_code(code):
    if code in __code_dic:
        return __code_dic[code]
    else:
        return ERROR_SERVICE


def err_by_msg(msg):
    if msg in __msg_dic:
        return __msg_dic[msg]
    else:
        return ERROR_SERVICE


class ErrorException(Exception):
    def __init__(self, error=OP_SUCCEEDED):
        self._error = error

    def get_msg(self):
        return self._error[1]

    def get_code(self):
        return self._error[0]

    def to_dict(self):
        return {'code': self.get_code(), 'msg': self.get_msg()}
