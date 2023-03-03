import json
import logging

from twisted.web.http import Request

from error_code import ErrorException, ERROR_INTERFACE_METHOD, OP_SUCCEEDED, err_by_code

match_rule = '/path/status'


def interface_function(request: Request) -> None:
    if request.method.decode() != 'POST':
        raise ErrorException(ERROR_INTERFACE_METHOD)

    res_obj = ErrorException(OP_SUCCEEDED).to_dict()
    res_obj['data'] = {"match_rule": match_rule}


    request.setResponseCode(200)
    request.responseHeaders.addRawHeader(b"content-type", b"application/json")
    request.write(json.dumps(res_obj).encode(encoding='utf_8'))
    request.finish()
