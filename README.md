# Stupid Server

基于 Python Twisted, 用于快速搭建提供 HTTP 协议的旁路服务.

### Feather
1. 基于 Python, 部署维护简单
2. 集成了日志及错误码
3. 支持通过路径来匹配接口
4. 支持动态增减改接口

### Quickstart
#### Get Code
````
git clone https://github.com/Phypeng/StupidServer.git
cd StupidServer
git checkout main
````
#### Start Service
##### Linux
###### CentOS
````
yum install python3 -y
pip3 install twisted

python3 http_service.py
````
###### Ubuntu
````
apt-get install python3 -y
pip3 install twisted

python3 http_service.py
````
##### Windows
###### Windows 11
````
安装 Python3
打开 CMD 输入 : pip3 install twisted

双击 http_service.py
````
#### Test Interface
1. 重新载入接口
    ````
    curl --location --request POST '127.0.0.1:8811/reload_interface'
    ````
   
2. 列举所有接口
    ````
    curl --location '127.0.0.1:8811/list_interface'
    ````

### More
[如何添加接口?](./docs/interface.md)

[如何部署?](./docs/deploy.md)

[关于 HTTP 服务](./docs/http_service.md)
