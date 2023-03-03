## 添加自定义接口

### 自定义接口文件是什么样的?
+ 接口文件为标准 Python 源文件, 以 '.py' 结尾
+ 其中必须包含一个名为 'match_rule' 的 'string' 类型变量, 用于描述接口的路径匹配规则
+ 其中必须包含一个函数签名为 'def interface_function(request: Request) -> None' 的方法
    
    ```python
    # interface/test.py
  
    match_rule = '/test/interface'
    
    
    def interface_function(request):
        pass
    ```

### 自定义接口文件放在哪?
+ 目录位置在 lib/http_server.py 中定义, 变量名为 'interface_path'
+ 'interface_path' 的名称可修改, 但不能与已安装模块重名.

### 如何加载新接口?
重启软件或调用 '管理服务(MGMT)' 中的 'reload_interface' 接口
  ````shell
  curl --location --request POST '127.0.0.1:8811/reload_interface'
  ````


### 详述
##### 1. 什么是 'match_rule' ?
+ 接口文件通过此变量描述将要匹配的路径 (HTTP 请求中的 PATH)

##### 2. ['match_rule' 都支持如何匹配路径 ?](./match_rule.md)

##### 3. [关于 interface_function](./interface_function.md)

##### 4. [关于日志](./logging.md)

##### 5. [关于配置文件](./config.md)
