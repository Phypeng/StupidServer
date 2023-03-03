"""
CMD:

curl --location '192.168.137.2:8801/test/request' \
--header 'Content-Type: application/json' \
--data '{"num": 10}'
"""


import json
import logging
import traceback


from error_code import ErrorException, \
    ERROR_INTERFACE_METHOD, \
    ERROR_INTERFACE_CONTENT_TYPE, \
    ERROR_INTERFACE_REQUEST_JSON_INVALID, OP_SUCCEEDED

from twisted.web.http import Request


match_rule = '/test/request'


def interface_function(request: Request):
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

        logging.debug(json.dumps(req_obj))
        exit(1)
    except ErrorException as e:
        logging.debug(f'ErrorCode:{e.get_code()}  ErrorMsg:{e.get_msg()}')
        logging.error(traceback.format_exc())
        res_obj = e.to_dict()

        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
        request.setResponseCode(200)
        request.finish()
    else:
        res_obj = ErrorException(OP_SUCCEEDED).to_dict()
        res_obj['data'] = req_obj

        request.setResponseCode(200)
        request.responseHeaders.addRawHeader(b"content-type", b"application/json")
        request.write(json.dumps(res_obj).encode(encoding='utf_8'))
        request.finish()
