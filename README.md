# Docker项目：ChatGPT API 平台

## 自行搭建

复制下列代码，并自行修改配置

```yaml
version: '3'

# GPL协议开源，禁止商用，禁止修改后闭源，禁止盈利！！！

services:
  web:
    image: sengedev/chatgpt:latest   # 镜像地址
    ports:
      - "5000:5000" # 端口号，如果端口冲突，请修改
    restart: always # 重启策略
    environment:
      API_KEY: YourOpenAIApiKey # 请替换为你的OpenAI API Key，前往https://platform.openai.com/account/api-keys获取
      HOUR_LIMIT: 50  # 限制每小时调用次数，如果不想限制，则不设置该变量
      MINUTE_LIMIT: 3 # 限制每分钟调用次数，如果不想限制，则不设置该变量
      SECOND_LIMIT: 1 # 限制每秒调用次数，如果不想限制，则不设置该变量
      ROUTE: api  # 路由，如果不想设置，则不设置该环境变量
    volumes:
      - ./logs:/app/logs # 日志保存路径
```

字段含义

| 字段         | 含义                                                         |
| ------------ | ------------------------------------------------------------ |
| volumes      | 持久化配置，文件映射                                         |
| API_KEY      | API密钥，配置后无需请求头即可完成调用，不建议设置，除非你开启了IP地址白名单 |
| HOUR_LIMIT   | 每小时调用次数限制，如果设置为0则无限制                      |
| MINUTE_LIMIT | 每分钟调用次数限制，如果设置为0则无限制                      |
| SECOND_LIMIT | 每秒调用次数限制，如果设置为0则无限制                        |
| ROUTE        | 例如你的网站是https://api.example.com ，路由为route，则请求链接为 https://api.example.com/route |

## 实例介绍

### 使用教程

下方是一个示例API地址，请替换为您自己的IP/域名。

API链接: https://api.example.com/

获取ChatGPT回答

请求方式：`GET`，路由：`/chatgpt`

#### 请求头

| 请求头 | 描述                                          | 是否必需 |
| ------ | --------------------------------------------- | -------- |
| ApiKey | ChatGPT的API密钥                              | 是`*1`   |
| Model  | ChatGPT API模型，默认使用text-davinci-003模型 | 否       |

#### 请求数据

| 数据   | 描述                | 是否必需 |
| ------ | ------------------- | -------- |
| prompt | 向ChatGPT发送的文本 | 是       |

#### 返回值

- 成功

```json
{
    "code": 200,
    "msg": "success",
    "data": {
        "response": "ChatGPT回答的内容"
    }
}
```

- 失败

```json
{
    "code": 4xx,
    "msg": "failed",
    "data": {
        "response": "请求失败的原因"
    }
}
```

- 常见返回值

| code | 描述                                                         |
| ---- | ------------------------------------------------------------ |
| 200  | 成功                                                         |
| 400  | 请求参数错误(API未填写或填写错误、模型使用错误、缺少prompt或prompt为空) |
| 401  | 未授权                                                       |
| 403  | 禁止访问                                                     |
| 404  | 请求路径不存在                                               |
| 500  | 服务器内部错误                                               |
| 429  | 请求过于频繁                                                 |

#### 默认调用次数限制（每个IP）

API完全开放使用，无需申请，但是需要自行申请API Key

| 时间段 | 频率   |
| ------ | ------ |
| 天     | 无限制 |
| 小时   | 50次   |
| 分钟   | 3次    |
| 秒     | 1次    |

## 示例代码

将https://api.example.com替换为你的服务器IP/域名地址

### Python（连续对话）

```python
import requests
import json
 
url = "https://chatgpt.example.com/api"
sys_prompt = input("sys> ")
 
continuous_dialogue = []
while True:
    user_input = input("user> ")
    if user_input.lower() in ['exit', 'quit']:
        break
    data = {
        "system_content": sys_prompt,
        "user_content": user_input,
        "model": "gpt-3.5-turbo",
        "api_key": "sk-U3y83c7o8nOn8i4ONnoT5uA9B6Yd75xrl9BIKihk4vCmCMzi",	# 该API为 fake API Key，请换成自己的API Key
        "continuous": [],
        "max_tokens": 100
    }
    response = requests.post(url, json=data)
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}")
        print(response.text)
    else:
        result = json.loads(response.text)
    print(f"ChatGPT回答：{result['current_response']}")
    # 连续对话迭代
    continuous_dialogue.append({"role": "user", "content": user_input})
    continuous_dialogue.append({"role": "assistant", "content": result['current_response']})
```

### Python（非连续对话）

```python
import requests
import json
 
url = "https://chatgpt.example.com/api"
sys_prompt = input("sys> ")
 
 
user_input = input("user> ")
data = {
    "system_content": sys_prompt,
    "user_content": user_input,
    "model": "gpt-3.5-turbo",
    "api_key": "sk-U3y83c7o8nOn8i4ONnoT5uA9B6Yd75xrl9BIKihk4vCmCMzi",	# 该API为 fake API Key，请换成自己的API Key
    "max_tokens": 100
}
response = requests.post(url, json=data)
if response.status_code != 200:
    print(f"请求失败，状态码：{response.status_code}")
    print(response.text)
else:
    result = json.loads(response.text)
print(f"ChatGPT回答：{result['current_response']}")
```
