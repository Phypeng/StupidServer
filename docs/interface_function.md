## 关于 interface_function


### 如何在 interface_function 中处理 Request
#### 导入模块
  ```python
  from twisted.web.http import Request
  ```
#### 解析请求 (详见 Twisted), 以下为一些常见操作:
+ 获取请求 PATH
  ```python
  request.path.decode()
  ```
+ 获取请求 METHOD
  ```python
  request.method.decode()
  ```
+ 获取请求中的所有 Header
  ```python
  for a in request.requestHeaders.getAllRawHeaders():
      pass
  ```
+ 获取请求 ARGS
  ```python
  request.args
  ```
+ 获取请求中的 Cookies
  ```python
  request.parseCookies()
  ```

+ 获取请求中指定的 Header
  ```python
  request.getHeader('Content-Type')
  ```
+ 获取请求中内容
  ```python
  request.content.getvalue()
  ```
+ 将请求中的内容解析为JSON
  ```python
  json.loads(request.content.getvalue().decode())
  ```
  

#### 结束请求的常见操作
+ 设置 Header
  ```python
  request.responseHeaders.addRawHeader(b"content-type", b"application/json")
  ```
+ 写入 JSON
  ```python
  res_obj = {}
  request.write(json.dumps(res_obj).encode(encoding='utf_8'))
  ```

+ 设置错误码
  ```python
  request.setResponseCode(200)
  ```
+ 结束返回
  ```python
  request.finish()
  ```


#### 一个例子
###### 接口示例
  ```python
  """
  CMD:
  
  curl --location '127.0.0.1:8801/test/request' \
  --header 'Content-Type: application/json' \
  --data '{"num": 10}'
  
  """
  
  import json
  import logging
  import traceback
  
  from twisted.web.http import Request
  
  from error_code import ErrorException, \
  ERROR_INTERFACE_METHOD, \
  ERROR_INTERFACE_CONTENT_TYPE, \
  ERROR_INTERFACE_REQUEST_JSON_INVALID, OP_SUCCEEDED
  
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
      except ErrorException as e:
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


  ```

###### 请求命令
```shell
curl --location '127.0.0.1:8801/test/request' \
--header 'Content-Type: application/json' \
--data '{"num": 10}'
```


###### 预期结果
```json
{
    "code": 0,
    "msg": "Operation-succeeded",
    "data": {
        "num": 10
    }
}
```

+ 该示例是一个简单的请求响应接口, 接收一个 JSON, 并将该 JSON 包装一下返回.
+ 推荐使用示例中通过异常来传递错误码的机制, 即通过 error_code.py 中的 ErrorException 将自定义错误以异常的方式抛出, 详见[自定义错误码](./error_code.md).
