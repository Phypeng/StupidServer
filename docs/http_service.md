## 关于 HTTP Service
+ 工程启动时运行了两个 HTTP Server, 一个用于管理 (MGMT), 一个用于承载用户接口 (Service).
+ MGMT 与 Service 的端口和监听地址均可在配置文件中设置.
+ 毋庸置疑, MGMT 与 Service 的端口是不能相同的.
+ 建议将 MGMT 的监听地址单独设置, 不要透露到业务网, 以防不测.


### MGMT 服务
**提供一套 HTTP 协议的管理/查询接口**

#### 目前提供的接口有

###### 重新载入接口
```shell
curl --location --request POST '127.0.0.1:8811/reload_interface' \
--data ''
```

###### 按优先级列举所有已载入的接口
```shell
curl --location '127.0.0.1:8811/list_interface' \
--data ''
```

###### 获取当前 Log 级别
```shell
curl --location -g '127.0.0.1:8811/get_log_level' \
--data ''
```

###### 设置 Log 级别
```shell
curl --location -g '127.0.0.1:8811/change_log_level' \
--header 'Content-Type: application/json' \
--data '{"log_level":"debug"}'
```