import json
import traceback

from twisted.web import server, resource
from twisted.web.http import Request
from twisted.internet import reactor

from lib.conf_tool import http_conf
from error_code import ErrorException, ERROR_SERVICE, ERROR_INTERFACE_METHOD, ERROR_INTERFACE_CONTENT_TYPE, \
    ERROR_INTERFACE_REQUEST_JSON_INVALID, ERROR_INTERFACE_PARAM, OP_SUCCEEDED
from lib.interface_manager import InterfaceManager
import logging

from lib.log_utils import switch_log_level, log_level_set


def interface_change_log_level(request: Request):
    try:
        if request.method.decode() != 'POST':
            raise ErrorException(ERROR_INTERFACE_METHOD)

        if request.getHeader('Content-Type') != 'application/json':
            raise ErrorException(ERROR_INTERFACE_CONTENT_TYPE)

        req_data = request.content.getvalue()

        try:
            req_obj = json.loads(req_data.decode())
        except (Exception,):
            raise ErrorException(ERROR_INTERFACE_REQUEST_JSON_INVALID)

        try:
            log_level = req_obj['log_level']
        except KeyError:
            raise ErrorException(ERROR_INTERFACE_PARAM)

        if not isinstance(log_level, str):
            raise ErrorException(ERROR_INTERFACE_PARAM)

        if log_level not in log_level_set:
            raise ErrorException(ERROR_INTERFACE_PARAM)

        http_conf.set('log', "log_level", log_level)

        logger = logging.getLogger()
        logger.setLevel(switch_log_level(log_level))
    except ErrorException as e:
        logging.error(traceback.format_exc())
        res_obj = e.to_dict()

        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
        request.setResponseCode(200)
        request.finish()
    else:
        res_obj = ErrorException(OP_SUCCEEDED).to_dict()

        request.setResponseCode(200)
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
        request.finish()


def interface_get_log_level(request: Request):
    try:
        if request.method.decode() != 'GET':
            raise ErrorException(ERROR_INTERFACE_METHOD)

        log_level = http_conf.get('log', "log_level")

    except ErrorException as e:
        logging.error(traceback.format_exc())
        res_obj = e.to_dict()

        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
        request.setResponseCode(200)
        request.finish()
    else:
        res_obj = ErrorException(OP_SUCCEEDED).to_dict()
        res_obj['data'] = {"log_level": log_level}

        request.setResponseCode(200)
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
        request.finish()


class MServer(resource.Resource):
    isLeaf = True
    __interface_manager = None

    def __init__(self, interface_manager: InterfaceManager):
        self.__interface_manager = interface_manager
        super().__init__()

    def reload_interface(self, request: Request):
        try:
            if request.method.decode() != 'POST':
                raise ErrorException(ERROR_INTERFACE_METHOD)

            result = self.__interface_manager.reload_interface()

        except ErrorException as e:
            logging.error(traceback.format_exc())
            res_obj = e.to_dict()

            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            request.write(json.dumps(res_obj).encode(encoding='utf_8'))
            request.setResponseCode(200)
            request.finish()
        else:
            res_obj = ErrorException(OP_SUCCEEDED).to_dict()
            res_obj['data'] = result

            request.setResponseCode(200)
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            request.write(json.dumps(res_obj).encode(encoding='utf_8'))
            request.finish()

    def list_interface(self, request: Request):
        try:
            if request.method.decode() != 'GET':
                raise ErrorException(ERROR_INTERFACE_METHOD)

            result = self.__interface_manager.list_interface()

        except ErrorException as e:
            logging.error(traceback.format_exc())
            res_obj = e.to_dict()

            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            request.write(json.dumps(res_obj).encode(encoding='utf_8'))
            request.setResponseCode(200)
            request.finish()
        else:
            res_obj = ErrorException(OP_SUCCEEDED).to_dict()
            res_obj['data'] = result

            request.setResponseCode(200)
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            request.write(json.dumps(res_obj).encode(encoding='utf_8'))
            request.finish()

    def __do_fun(self, request: Request):
        try:
            if request.path.decode() == "/reload_interface":
                self.reload_interface(request)
            elif request.path.decode() == "/change_log_level":
                interface_change_log_level(request)
            elif request.path.decode() == "/get_log_level":
                interface_get_log_level(request)
            elif request.path.decode() == "/list_interface":
                self.list_interface(request)
            else:
                request.setResponseCode(404)
                request.finish()

        except Exception as e:
            logging.error('MServer Exception path:%s Exception:%s\n %s' %
                          (request.path.decode(), repr(e), traceback.format_exc()))

            res_obj = {'status': 0, 'msg': ErrorException(ERROR_SERVICE).get_msg()}
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            request.write(json.dumps(res_obj).encode(encoding='utf_8'))
            request.setResponseCode(200)
            request.finish()

    def render(self, request):
        reactor.callInThread(self.__do_fun, request)
        return server.NOT_DONE_YET
