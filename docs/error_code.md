## ErrorCode 的定义与传递机制

### 为什么不使用 HTTP Error Code 来传递错误码?
不够统一, 不便套用.


### 为什么使用异常来传递错误码?
+ 便于子方法的错误收集, 不需要一层一层的判断/传递返回值.
+ 便于排查问题, 分层明显, 结构简单.

### 关于 Error Code
+ 推荐 HTTP 请求的返回结果为以下形式, code 字段描述错误码 (必填), msg 字段描述错误信息 (必填), data 字段为实际返回结果 (选填).
    ```json
    {
        "code": 0,
        "msg": "Operation-succeeded",
        "data": {
            "num": 10
        }
    }
    ```
+ 错误码全部定义在工程目录下的 error_code.py 中.

+ 错误码使用 Python 中的 tuple 类型定义, 第一个变量为整形错误码, 第二个变量为字符串型描述信息, 按需添加, 如下:
    ```python
    ERROR_SERVICE = (-4, 'ERROR-SERVICE')
    ```
  
+ 整形的错误码主要便于接口间的错误码转换, 可以通过 error_code.py 中的 err_by_code(code) 来将整形转换为内部错误码.
  ```python
  if ERROR_INTERFACE_METHOD == err_by_code(code):
      pass
  ```
  
+ 字符串的错误信息主要便于人类识别, 可以通过 error_code.py 中的 err_by_msg(msg) 来将字符串转换为内部错误码.
  ```python
  if ERROR_INTERFACE_METHOD == err_by_msg(msg):
      pass
  ```
  
+ 可以通过 error_cede.py 中 ErrorException 的 get_msg() 和 get_code() 获取需要的错误信息.
  ```python
      try:
          do_something()
      except ErrorException as e:
          logging.debug(f'ErrorCode:{e.get_code()}  ErrorMsg:{e.get_msg()}')
  ```

+ 可以通过 error_cede.py 中 ErrorException 的 to_dict(), 将错误信息转换为 JSON 返回值.
  ```python
      try:
          do_something()
      except ErrorException as e:
          res_obj = e.to_dict()
  
          request.responseHeaders.addRawHeader(b"content-type", b"application/json")
          request.write(json.dumps(res_obj).encode(encoding='utf_8'))
          request.setResponseCode(200)
          request.finish()
  ```

+ 错误码以异常的形式通过 error_code.py 中的 ErrorException 抛出:
    ```python
    raise ErrorException(ERROR_INTERFACE_METHOD)
    ```
  
+ 在外层函数调用自定义接口中的 interface_function 时, 会捕获 ErrorException 类型的异常, 并调用 ErrorException 的 to_dict() 方法将异常转换为 JSON 返回.
  ```python
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
      ......
  finally:
      ......
  ```
  
+ 在外层函数调用自定义接口中的 interface_function 时, 会捕获所有 BaseException 异常, 此时, 框架会认为接口发生致命错误, 将其视为 ERROR_SERVICE_INTERFACE 异常.
  ```python
  try:
      interface_function(request)
  except ErrorException as e:
      ......
  except BaseException as e:
      logging.error('Interface Exception path:%s Exception:%s\n %s' %
                    (request.path.decode(), repr(e), traceback.format_exc()))
  
      res_obj = ErrorException(ERROR_SERVICE_INTERFACE).to_dict()
  
      request.responseHeaders.addRawHeader(b"content-type", b"application/json")
      request.write(json.dumps(res_obj).encode(encoding='utf_8'))
      request.setResponseCode(200)
      request.finish()
  finally:
      ......
  ```

+ 在外层函数调用自定义接口中的 interface_function 后, 发现 Request 并未 Finished 时, 框架亦会认为接口发生致命错误, 将其视为 ERROR_SERVICE_INTERFACE 异常.
  ```python
  try:
      interface_function(request)
  except ErrorException as e:
      ......
  except BaseException as e:
      ......
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
  ```

+ 除了直接将异常抛给外部, 更好的做法是在接口内处理自定义异常, 如需要:
  + 对子方法中的异常进行特殊操作,如回滚.
  + 对接口的返回值有特殊要求, 如异常的请求需要返回特定的数据.
  ```python
    try:
        # 做想做的事, 可预想的错误以 ErrorException 抛出.
        # 应杜绝抛出非 ErrorException 异常, 除非清楚的知道如何处理.
        do_something()
    except ErrorException as e:
        # 处理自定义的异常
    else:
        pass
    finally:
        pass
   ```
  
+ error_code.py 中的 '错误码' 和 '错误信息' 不能重复, 否则会触发断言.
