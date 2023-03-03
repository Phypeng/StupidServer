## Match_Rule 规则

### 支持的匹配类型

+ 绝对路径匹配   
  形如 : '/path/status', 匹配情况如下 :

  | 实际路径          |能否匹配|
  |------------------|------|
  | /path/status     | Yes  |
  | /path/status/    | No   |
  | /path/status/log | No   |
  | /path/stat       | No   |
  | /path/           | No   |
  | /path            | No   |

+ 参数匹配   
  形如 : '/path/{}/status', 匹配情况如下 :

  | 实际路径                 | 能否匹配 |
  |:---------------------|:-----|
  | /path/user/status    | Yes  |
  | /path/system/status  | Yes  |
  | /path/system/status/ | No   |
  | /path/system/stat    | No   |
  | /path/status         | No   |

+ 前缀匹配   
  形如 : '/path/*', 匹配情况如下 :

  | 实际路径              | 能否匹配 |
  |:------------------|:-----|
  | /path/user0       | Yes  |
  | /path/user0/file0 | Yes  |
  | /path/            | Yes  |
  | /path             | No   |



### 命名规则

#### 1. 路径以 '/' 开头

  | match_rule      | 是否合法 |
  |-----------------|------|
  | /path           | Yes  |
  | path            | No   |
  | path/status/log | No   |

#### 2. 不能以 '/' 结尾

  | match_rule        | 是否合法 |
  |-------------------|------|
  | /path             | Yes  |
  | /path/            | No   |
  | /path/status/log/ | No   |

#### 3. 共支持两种参数占位符 '{}' 和 '/':
###### 3.1. 参数占位符前后只能是 '/',否则按绝对路径匹配.

| match_rule      | 匹配规则   |
|-----------------|--------|
| /path/{}        | 参数匹配   |
| /path/info_{}   | 绝对路径匹配 |
| /path/{}_status | 绝对路径匹配 |
| /path/*         | 前缀匹配   |
| /path/info_*    | 绝对路径匹配 |
| /path/*_status  | 绝对路径匹配 |

###### 3.2. 用于匹配单个参数, 路径中可以包含多个 '{}';

| match_rule         | 匹配规则 |
--------------------|--------------------|
| /path/{}           | 参数匹配  |
| /path/{}/status/{} | 参数匹配  |

###### 3.3. '*' 用于匹配前缀. 该参数只能位于路径最后. 该参数可以与 '{}' 混合使用;

| match_rule        | 匹配规则          |
-------------------|-------------------|
| /path/*           | 前缀匹配          |
| /path/*/status    | 绝对路径匹配        |
| /path/{}/status/* | 绝对路径匹配 + 前缀匹配 |


### 优先级及路径实际匹配情况的示例
| 优先级排序(从高到低)       |
|-------------------|
| /info/*/status/*  |
| /info/{}/status/* |
| /path/{}/info     |
| /test/interface   |
| /path/status      |
| /path/{}          |
| /path/*           |


| 请求的实际路径                                  | 匹配到的规则            |
|:-----------------------------------------|:------------------|
| {{service_url}}/info/*/status/*          | /info/*/status/*  |
| {{service_url}}/info/*/status/success    | /info/*/status/*  |
| {{service_url}}/info/user/status/success | /info/{}/status/* |
| {{service_url}}/info/user/status/        | /info/{}/status/* |
| {{service_url}}/info/user/status         | [404]             |
| {{service_url}}/path/user/info           | /path/{}/info     |
| {{service_url}}/path/user/infos          | /path/*           |
| {{service_url}}/path/status              | /path/status      |
| {{service_url}}/path/stat                | /path/{}          |
| {{service_url}}/path/stat/               | /path/*           |
| {{service_url}}/path/                    | /path/{}          |
