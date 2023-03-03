import json
import traceback

from twisted.web import server, resource
from twisted.web.http import Request
from twisted.internet import reactor

from error_code import ErrorException, ERROR_SERVICE_INTERFACE, ERROR_SERVICE, \
    ERROR_INTERFACE_NOT_FINISHED
from lib.interface_manager import InterfaceManager
import logging


# 除上传下载外, 能识别的错误均使用 200,错误信息在 json 中体现
class SServer(resource.Resource):
    isLeaf = True
    __interface_manager = None

    def __init__(self, interface_manager: InterfaceManager):
        self.__interface_manager = interface_manager
        super().__init__()

    def __do_fun(self, request: Request):
        try:
            interface_function = self.__interface_manager.match_interface(request.path.decode())
            if interface_function is None:
                logging.debug('Interface Not Found path:%s\n %s' %
                              (request.path.decode(), traceback.format_exc()))
                request.setResponseCode(404)
                request.finish()
            else:
                try:
                    interface_function(request)
                except ErrorException as e:
                    logging.debug(traceback.format_exc())
                    res_obj = e.to_dict()

                    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
                    request.write(json.dumps(res_obj).encode(encoding='utf_8'))
                    request.setResponseCode(200)
                    request.finish()
                except BaseException as e:
                    logging.error('Interface Exception path:%s Exception:%s\n %s' %
                                  (request.path.decode(), repr(e), traceback.format_exc()))

                    res_obj = ErrorException(ERROR_SERVICE_INTERFACE).to_dict()

                    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
                    request.write(json.dumps(res_obj).encode(encoding='utf_8'))
                    request.setResponseCode(200)
                    request.finish()
                finally:
                    if request.finished != 1:
                        e = ErrorException(ERROR_INTERFACE_NOT_FINISHED)
                        logging.error('Interface Exception path:%s Exception:%s\n %s' %
                                      (request.path.decode(), e.get_msg(), traceback.format_exc()))

                        res_obj = e.to_dict()

                        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
                        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
                        request.setResponseCode(200)
                        request.finish()
        except BaseException as e:
            logging.error('SServer Exception path:%s Exception:%s\n %s' %
                          (request.path.decode(), repr(e), traceback.format_exc()))

            res_obj = {'status': 0, 'msg': ErrorException(ERROR_SERVICE).get_msg()}
            request.responseHeaders.addRawHeader(b"content-type", b"application/json")
            request.write(json.dumps(res_obj).encode(encoding='utf_8'))
            request.setResponseCode(200)
            request.finish()
            return

    def render(self, request):
        reactor.callInThread(self.__do_fun, request)
        return server.NOT_DONE_YET
