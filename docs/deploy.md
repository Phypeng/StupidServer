## 部署方式

### 环境依赖
    1. Python 3
    2. Twisted `pip install twisted`

### 推荐的使用方式

#### 手动启动
`cd StupidServer && python3 http_service.py`

#### Linux 服务启动
###### 将工程放在 /opt/StupidServer 中 (根据需要更改工程目录名称).
###### 服务配置文件 (/usr/lib/systemd/system/stupid_server.service)
```
[Unit]
Description=Stupid HTTP Server
After=network.target
After=network-online.target
Wants=network-online.target
 
[Service]
Type=simple
WorkingDirectory=/opt/StupidServer
ExecStart=/usr/bin/python3 /opt/StupidServer/http_service.py
Restart=on-failure
LimitNOFILE=65536
 
[Install]
WantedBy=multi-user.target
```

###### 启动服务
```shell
service stupid_server start
```

###### 查看服务状态
```shell
service stupid_server status
```

###### 停止服务
```shell
service stupid_server stop
```

###### 重启服务
```shell
service stupid_server restart
```

###### 服务自启动
```shell
systemctl enable stupid_server
```

#### 容器启动
大同小异,略

